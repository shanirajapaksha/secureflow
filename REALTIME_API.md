# SecureFlow-AI Real-Time API Setup

This backend captures packets with TShark, converts PCAP files to CICFlowMeter V4 flows, and runs hybrid intrusion detection. The React UI is available at `/realtime`.

## 1. Check Wireshark/TShark

```powershell
& "C:\Program Files\Wireshark\tshark.exe" -D
```

The API can also list interfaces:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/realtime/interfaces
```

## 2. Build CICFlowMeter (Windows)

The project includes CICFlowMeter source and automatically detects its generated CLI launcher. Install Temurin JDK 8 and build it once:

```powershell
winget install --id EclipseAdoptium.Temurin.8.JDK --exact
powershell -ExecutionPolicy Bypass -File .\tools\build_cicflowmeter.ps1
```

Check the converter:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/realtime/converter/status
```

## 3. Optional External CICFlowMeter

Install or download a CICFlowMeter CLI/JAR, then set `CICFLOWMETER_CMD`.

Example:

```powershell
$env:CICFLOWMETER_CMD = 'java -jar "C:\tools\CICFlowMeter\CICFlowMeter.jar" "{input}" "{output_dir}"'
```

The command must accept:

- `{input}`: pcap or pcapng capture file path
- `{output_dir}`: folder where flow CSV files are written

## 4. Capture Then Analyze

List interfaces first and choose Wi-Fi/Ethernet.

```powershell
$body = @{ interface = "5"; duration_seconds = 10 } | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/realtime/capture-and-analyze `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

## 5. Dashboard

Open `http://localhost:8080/realtime`, select the Wi-Fi/Ethernet interface, choose a duration, and use either:

- **Capture & Analyze** for a timed capture.
- **Start** for continuous monitoring. The backend repeatedly captures and analyzes windows using the selected duration; use **Stop Monitoring** to end the loop.

The page polls status and recent alerts every two seconds, so cards, charts, and the alert table update after every completed capture window without stopping monitoring.

## 6. Manual Flow CSV Ingest

If you convert pcap files manually with CICFlowMeter, upload the output CSV:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/realtime/ingest-flow-csv `
  -Method Post `
  -Form @{ file = Get-Item ".\flow_output.csv" }
```

Recent alerts:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/realtime/alerts
```
