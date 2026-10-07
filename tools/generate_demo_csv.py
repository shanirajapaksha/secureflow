"""Create a model-compatible CSV for the SecureFlow-AI final demo."""
from pathlib import Path

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "data" / "processed" / "preprocessing_artifacts.joblib"
OUTPUT = ROOT / "data" / "demo" / "secureflow_demo_traffic.csv"


def row(name: str, source_ip: str, **values: float | int | str) -> dict:
    record = {column: 0 for column in SELECTED_COLUMNS}
    record.update(
        {
            "Demo_Scenario": name,
            "Timestamp": "2026-10-06T10:00:00Z",
            "Source IP": source_ip,
            "Destination Port": 443,
            "Flow Duration": 100_000,
            "Total Fwd Packets": 10,
            "Total Backward Packets": 10,
            "Total Length of Fwd Packets": 5_000,
            "Total Length of Bwd Packets": 4_000,
            "Flow Bytes/s": 90_000,
            "Flow Packets/s": 200,
            "SYN Flag Count": 1,
            "ACK Flag Count": 10,
        }
    )
    record.update(values)
    return record


SELECTED_COLUMNS = list(joblib.load(ARTIFACTS)["selected_columns"])
records = [
    row("Normal HTTPS traffic", "192.168.1.10"),
    row("DDoS signature", "203.0.113.10", **{"Destination Port": 80, "Flow Packets/s": 15_000, "Flow Bytes/s": 2_000_000}),
    row("SYN flood signature", "203.0.113.11", **{"Destination Port": 443, "SYN Flag Count": 35, "Flow Packets/s": 4_000}),
    row("Port scan signature", "203.0.113.12", **{"Destination Port": 22, "Flow Duration": 30_000, "Total Fwd Packets": 3, "Total Backward Packets": 2}),
    row("FTP brute-force signature", "203.0.113.13", **{"Destination Port": 21, "Flow Packets/s": 800, "Flow Bytes/s": 200_000}),
    row("High-rate review traffic", "203.0.113.14", **{"Destination Port": 8080, "Flow Bytes/s": 1_500_000, "Flow Packets/s": 500}),
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(records).to_csv(OUTPUT, index=False)
print(OUTPUT)
