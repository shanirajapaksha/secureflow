from datetime import datetime, timezone
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import threading
import time
from typing import Any, Callable

import pandas as pd
from fastapi import HTTPException

from .config import Settings, settings
from .detection import DetectionService, utc_now


def find_java() -> str | None:
    found = shutil.which("java")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\Eclipse Adoptium\jdk-17\bin\java.exe",
        r"C:\Program Files\Java\jdk-17\bin\java.exe",
        r"C:\Program Files\Java\jre-1.8\bin\java.exe",
        r"C:\Program Files (x86)\Java\jre-1.8\bin\java.exe",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def find_tshark() -> str | None:
    found = shutil.which("tshark")
    if found:
        return found
    for candidate in (
        r"C:\Program Files\Wireshark\tshark.exe",
        r"C:\Program Files (x86)\Wireshark\tshark.exe",
    ):
        if os.path.exists(candidate):
            return candidate
    return None


def find_converter_template(app_settings: Settings = settings) -> str | None:
    configured = os.getenv("CICFLOWMETER_CMD")
    if configured:
        return configured

    configured_jar = os.getenv("CICFLOWMETER_JAR")
    if configured_jar and Path(configured_jar).is_file() and find_java():
        return f'"{find_java()}" -jar "{configured_jar}" "{{input}}" "{{output_dir}}"'

    for candidate in (
        app_settings.base_dir / "tools" / "CICFlowMeter" / "CICFlowMeter.jar",
        app_settings.base_dir / "tools" / "cicflowmeter" / "CICFlowMeter.jar",
        app_settings.base_dir / "CICFlowMeter.jar",
    ):
        if candidate.is_file() and find_java():
            return f'"{find_java()}" -jar "{candidate}" "{{input}}" "{{output_dir}}"'

    bundled_launchers = (
        app_settings.base_dir
        / "tools"
        / "CICFlowMeter-src-20260820"
        / "CICFlowMeter-master"
        / "build"
        / "install"
        / "CICFlowMeter"
        / "bin"
        / "cfm.bat",
        app_settings.base_dir / "tools" / "CICFlowMeter" / "bin" / "cfm.bat",
    )
    for launcher in bundled_launchers:
        if launcher.is_file():
            return f'"{launcher}" "{{input}}" "{{output_dir}}"'

    executable = shutil.which("cicflowmeter") or shutil.which("cfm")
    return f'"{executable}" "{{input}}" "{{output_dir}}"' if executable else None


def command_arguments(template: str, capture: Path, output_dir: Path) -> list[str]:
    rendered = template.format(input=str(capture), output_dir=str(output_dir), output=str(output_dir))
    tokens = shlex.split(rendered, posix=os.name != "nt")
    if os.name == "nt":
        tokens = [token[1:-1] if len(token) > 1 and token[0] == token[-1] and token[0] in "\"'" else token for token in tokens]
    return tokens


def parse_interfaces(output: str) -> list[dict[str, str]]:
    interfaces = []
    for raw in output.splitlines():
        line = raw.strip()
        if "." not in line:
            continue
        number, name = line.split(".", 1)
        if number.strip().isdigit():
            interfaces.append({"id": number.strip(), "name": name.strip(), "raw": line})
    return interfaces


def local_capture_interfaces(output: str, platform_name: str | None = None) -> list[dict[str, str]]:
    interfaces = parse_interfaces(output)
    if (platform_name or os.name) == "nt":
        return [item for item in interfaces if item["name"].startswith("\\Device\\NPF_")]
    return interfaces


class RealtimeService:
    def __init__(
        self,
        detector: DetectionService,
        app_settings: Settings = settings,
        persistence_callback: Callable[[str | None, str | None, dict[str, Any]], None] | None = None,
    ):
        self.detector = detector
        self.settings = app_settings
        self.persistence_callback = persistence_callback
        self.lock = threading.RLock()
        self.monitor_stop = threading.Event()
        self.state: dict[str, Any] = {
            "running": False,
            "process": None,
            "interface": None,
            "capture_file": None,
            "started_at": None,
            "stopped_at": None,
            "last_error": None,
            "recent_alerts": [],
            "monitoring": False,
            "processing": False,
            "monitor_thread": None,
        }

    def serialize(self) -> dict[str, Any]:
        with self.lock:
            process = self.state["process"]
            process_running = bool(process and process.poll() is None)
            running = bool(self.state["monitoring"] or process_running)
            if process and not process_running and self.state["running"] and not self.state["monitoring"]:
                self.state["running"] = False
                self.state["stopped_at"] = utc_now()
                if process.returncode and process.stderr:
                    self.state["last_error"] = process.stderr.read().strip() or f"TShark exited with code {process.returncode}."
            return {
                "running": running,
                "interface": self.state["interface"],
                "capture_file": self.state["capture_file"],
                "started_at": self.state["started_at"],
                "stopped_at": self.state["stopped_at"],
                "last_error": self.state["last_error"],
                "recent_alert_count": len(self.state["recent_alerts"]),
                "monitoring": self.state["monitoring"],
                "processing": self.state["processing"],
            }

    def converter_status(self) -> dict[str, Any]:
        command = find_converter_template(self.settings)
        jar = os.getenv("CICFLOWMETER_JAR")
        return {
            "configured": command is not None,
            "command": command,
            "java_path": find_java(),
            "cicflowmeter_cmd_env_set": bool(os.getenv("CICFLOWMETER_CMD")),
            "cicflowmeter_jar": jar,
            "cicflowmeter_jar_exists": bool(jar and Path(jar).is_file()),
            "hint": None if command else "Set CICFLOWMETER_JAR or CICFLOWMETER_CMD with {input} and {output_dir} placeholders.",
        }

    def interfaces(self) -> dict[str, Any]:
        tshark = find_tshark()
        if not tshark:
            raise HTTPException(status_code=503, detail="TShark was not found. Install Wireshark with TShark or add it to PATH.")
        try:
            result = subprocess.run([tshark, "-D"], capture_output=True, text=True, timeout=15, check=True)
        except subprocess.CalledProcessError as exc:
            raise HTTPException(status_code=500, detail=exc.stderr.strip() or "Failed to list TShark interfaces.") from exc
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail="TShark interface listing timed out.") from exc
        return {"tshark_path": tshark, "interfaces": local_capture_interfaces(result.stdout), "raw_output": result.stdout}

    def start(
        self,
        interface: str,
        duration_seconds: int | None = None,
        window_seconds: int = 5,
    ) -> dict[str, Any]:
        tshark = find_tshark()
        if not tshark:
            raise HTTPException(status_code=503, detail="TShark was not found. Install Wireshark with TShark or add it to PATH.")
        if os.name == "nt":
            try:
                listed = subprocess.run([tshark, "-D"], capture_output=True, text=True, timeout=15, check=True)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
                raise HTTPException(status_code=500, detail="Could not validate the selected capture interface.") from exc
            allowed = local_capture_interfaces(listed.stdout)
            allowed_values = (
                {item["id"] for item in allowed}
                | {item["name"] for item in allowed}
                | {item["name"].split(" ", 1)[0] for item in allowed}
            )
            if interface not in allowed_values:
                raise HTTPException(
                    status_code=400,
                    detail="Select a local Wi-Fi/Ethernet Npcap interface; external interfaces such as wifidump are not supported.",
                )

        if duration_seconds is None:
            return self._start_monitor(interface, window_seconds)

        with self.lock:
            current = self.state["process"]
            if current and current.poll() is None:
                raise HTTPException(status_code=409, detail="A real-time capture is already running.")

            started = datetime.now(timezone.utc)
            # CICFlowMeter's bundled jNetPcap reader accepts classic PCAP, not
            # Wireshark's default PCAPNG format.
            capture = self.settings.live_dir / f"capture_{started.strftime('%Y%m%d_%H%M%S')}.pcap"
            command = [tshark, "-i", interface, "-F", "pcap", "-w", str(capture)]
            if duration_seconds:
                command.extend(["-a", f"duration:{duration_seconds}"])
            try:
                process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
            except OSError as exc:
                self.state["last_error"] = str(exc)
                raise HTTPException(status_code=500, detail=f"Failed to start TShark capture: {exc}") from exc
            time.sleep(0.5)
            if process.poll() is not None:
                error = process.stderr.read().strip() if process.stderr else "TShark exited immediately."
                self.state["last_error"] = error
                raise HTTPException(status_code=500, detail=error)
            self.state.update(
                running=True,
                process=process,
                interface=interface,
                capture_file=str(capture),
                started_at=started.isoformat().replace("+00:00", "Z"),
                stopped_at=None,
                last_error=None,
                recent_alerts=[],
            )
            return self.serialize()

    def _start_monitor(self, interface: str, window_seconds: int) -> dict[str, Any]:
        with self.lock:
            current = self.state["process"]
            if self.state["monitoring"] or (current and current.poll() is None):
                raise HTTPException(status_code=409, detail="A real-time capture is already running.")

            self.monitor_stop.clear()
            self.state.update(
                running=True,
                monitoring=True,
                processing=False,
                process=None,
                interface=interface,
                capture_file=None,
                started_at=utc_now(),
                stopped_at=None,
                last_error=None,
                recent_alerts=[],
            )
            thread = threading.Thread(
                target=self._monitor_loop,
                args=(interface, window_seconds),
                name="secureflow-realtime-monitor",
                daemon=True,
            )
            self.state["monitor_thread"] = thread
            thread.start()
            return self.serialize()

    def _monitor_loop(self, interface: str, window_seconds: int) -> None:
        tshark = find_tshark()
        try:
            while not self.monitor_stop.is_set():
                started = datetime.now(timezone.utc)
                capture = self.settings.live_dir / f"capture_{started.strftime('%Y%m%d_%H%M%S_%f')}.pcap"
                command = [
                    tshark,
                    "-i",
                    interface,
                    "-F",
                    "pcap",
                    "-w",
                    str(capture),
                    "-a",
                    f"duration:{window_seconds}",
                ]
                try:
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    with self.lock:
                        self.state.update(
                            process=process,
                            capture_file=str(capture),
                            started_at=started.isoformat().replace("+00:00", "Z"),
                            last_error=None,
                        )
                    try:
                        process.wait(timeout=window_seconds + 15)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                        raise HTTPException(status_code=504, detail="TShark capture window timed out.")

                    if process.returncode and not self.monitor_stop.is_set():
                        error = process.stderr.read().strip() if process.stderr else ""
                        raise HTTPException(status_code=500, detail=error or f"TShark exited with code {process.returncode}.")

                    if capture.is_file() and capture.stat().st_size >= 24 and not self.monitor_stop.is_set():
                        with self.lock:
                            self.state["processing"] = True
                        self.process_capture(str(capture))
                    elif not self.monitor_stop.is_set():
                        raise HTTPException(status_code=500, detail="TShark did not create a valid capture window.")
                except HTTPException as exc:
                    with self.lock:
                        self.state["last_error"] = str(exc.detail)
                    if not self.monitor_stop.is_set():
                        time.sleep(1)
                except Exception as exc:  # keep the monitor observable instead of silently dying
                    with self.lock:
                        self.state["last_error"] = str(exc)
                    if not self.monitor_stop.is_set():
                        time.sleep(1)
                finally:
                    with self.lock:
                        self.state["processing"] = False
                        self.state["process"] = None
        finally:
            with self.lock:
                self.state["monitoring"] = False
                self.state["running"] = False
                self.state["processing"] = False
                self.state["process"] = None
                self.state["stopped_at"] = utc_now()

    def stop(self) -> dict[str, Any]:
        with self.lock:
            process = self.state["process"]
            monitor_thread = self.state["monitor_thread"]
            self.monitor_stop.set()

        if process and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)

        if monitor_thread and monitor_thread.is_alive() and monitor_thread is not threading.current_thread():
            monitor_thread.join(timeout=self.settings.converter_timeout_seconds + 15)

        with self.lock:
            self.state["running"] = False
            self.state["monitoring"] = False
            self.state["processing"] = False
            self.state["stopped_at"] = utc_now()
            return self.serialize()

    def remember(self, predictions: list[dict[str, Any]]) -> None:
        received_at = utc_now()
        with self.lock:
            self.state["recent_alerts"].extend({**row, "Received_At": received_at} for row in predictions)
            self.state["recent_alerts"] = self.state["recent_alerts"][-self.settings.max_recent_alerts :]

    def alerts(self, limit: int) -> dict[str, Any]:
        safe_limit = max(1, min(limit, self.settings.max_recent_alerts))
        with self.lock:
            alerts = self.state["recent_alerts"][-safe_limit:]
            return {"count": len(alerts), "alerts": alerts}

    def _safe_capture(self, supplied: str | None) -> Path:
        if supplied:
            candidate = Path(supplied)
            if not candidate.is_absolute():
                candidate = self.settings.live_dir / candidate
            candidate = candidate.resolve()
            try:
                candidate.relative_to(self.settings.live_dir.resolve())
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Capture file must be inside data/live.") from exc
            if candidate.suffix.lower() not in {".pcap", ".pcapng"}:
                raise HTTPException(status_code=400, detail="Capture file must use .pcap or .pcapng.")
            if not candidate.is_file():
                raise HTTPException(status_code=404, detail=f"Capture file not found: {candidate.name}")
            return candidate

        with self.lock:
            current = self.state["capture_file"]
        if current and Path(current).is_file():
            return Path(current)
        captures = list(self.settings.live_dir.glob("*.pcap")) + list(self.settings.live_dir.glob("*.pcapng"))
        if not captures:
            raise HTTPException(status_code=404, detail="No capture file found. Start and stop a capture first.")
        return max(captures, key=lambda path: path.stat().st_mtime)

    def process_capture(self, supplied: str | None = None) -> dict[str, Any]:
        capture = self._safe_capture(supplied)
        if capture.suffix.lower() == ".pcapng":
            tshark = find_tshark()
            if not tshark:
                raise HTTPException(status_code=503, detail="TShark is required to convert PCAPNG to PCAP.")
            converted = capture.with_suffix(".pcap")
            result = subprocess.run(
                [tshark, "-r", str(capture), "-F", "pcap", "-w", str(converted)],
                capture_output=True,
                text=True,
                timeout=60,
                check=False,
            )
            if result.returncode:
                raise HTTPException(status_code=500, detail=result.stderr.strip() or "PCAPNG conversion failed.")
            capture = converted
        template = find_converter_template(self.settings)
        if not template:
            raise HTTPException(status_code=503, detail="CICFlowMeter is not configured. Set CICFLOWMETER_JAR or CICFLOWMETER_CMD.")
        output_dir = self.settings.live_dir / "flows" / capture.stem
        output_dir.mkdir(parents=True, exist_ok=True)
        started_at = time.time()
        arguments = command_arguments(template, capture, output_dir)
        launcher = Path(arguments[0])
        working_directory = str(launcher.parent) if launcher.is_file() else None
        converter_environment = os.environ.copy()
        if os.name == "nt":
            npcap_directory = Path(os.environ.get("WINDIR", r"C:\Windows")) / "System32" / "Npcap"
            if npcap_directory.is_dir():
                converter_environment["PATH"] = f"{npcap_directory}{os.pathsep}{converter_environment.get('PATH', '')}"
        try:
            result = subprocess.run(
                arguments,
                capture_output=True,
                text=True,
                timeout=self.settings.converter_timeout_seconds,
                check=False,
                cwd=working_directory,
                env=converter_environment,
            )
        except subprocess.TimeoutExpired as exc:
            raise HTTPException(status_code=504, detail="CICFlowMeter conversion timed out.") from exc
        if result.returncode:
            raise HTTPException(status_code=500, detail=result.stderr.strip() or result.stdout.strip() or "CICFlowMeter conversion failed.")
        candidates = [path for path in output_dir.glob("*.csv") if path.stat().st_mtime >= started_at]
        if not candidates:
            candidates = list(output_dir.glob("*.csv"))
        if not candidates:
            raise HTTPException(status_code=500, detail="CICFlowMeter finished but did not create a flow CSV.")
        flow_csv = max(candidates, key=lambda path: path.stat().st_mtime)
        response = self.detector.predict(pd.read_csv(flow_csv))
        self.remember(response["predictions"])
        if self.persistence_callback:
            self.persistence_callback(str(capture), str(flow_csv), response)
        return {
            "conversion": {"capture_file": str(capture), "flow_csv": str(flow_csv), "output_dir": str(output_dir)},
            **response,
        }

    def capture_and_analyze(self, interface: str, duration_seconds: int) -> dict[str, Any]:
        state = self.start(interface, duration_seconds=duration_seconds)
        deadline = time.time() + duration_seconds + 20
        while time.time() < deadline:
            if not self.serialize()["running"]:
                capture = Path(state["capture_file"])
                if not capture.is_file() or capture.stat().st_size < 24:
                    detail = self.state.get("last_error") or "TShark stopped without creating a valid capture file."
                    raise HTTPException(status_code=500, detail=detail)
                return self.process_capture(state["capture_file"])
            time.sleep(0.5)
        self.stop()
        raise HTTPException(status_code=504, detail="Capture did not stop before the processing timeout.")
