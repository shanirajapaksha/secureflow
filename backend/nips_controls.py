"""Explicit ICMP and SSH emergency controls retained from the legacy NIPS UI."""
from __future__ import annotations
import os
import platform
import subprocess

_active: set[str] = set()

def set_control(protocol: str, enabled: bool) -> bool:
    if protocol not in {"icmp", "ssh"}:
        raise ValueError("Protocol must be icmp or ssh.")
    if os.getenv("FIREWALL_ENFORCEMENT", "false").lower() != "true":
        (_active.add if enabled else _active.discard)(protocol)
        return False
    name = f"SecureFlow-NIPS-{protocol.upper()}"
    if platform.system() == "Windows":
        if enabled:
            args = ["netsh", "advfirewall", "firewall", "add", "rule", f"name={name}", "dir=in", "action=block", "protocol=icmpv4" if protocol == "icmp" else "protocol=TCP", *( ["localport=22"] if protocol == "ssh" else [])]
        else:
            args = ["netsh", "advfirewall", "firewall", "delete", "rule", f"name={name}"]
    else:
        args = ["iptables", "-I" if enabled else "-D", "INPUT", "-p", "icmp" if protocol == "icmp" else "tcp", *( ["--dport", "22"] if protocol == "ssh" else []), "-j", "DROP"]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "Firewall command failed.")
    (_active.add if enabled else _active.discard)(protocol)
    return True

def status() -> dict[str, bool]:
    return {"icmp": "icmp" in _active, "ssh": "ssh" in _active}
