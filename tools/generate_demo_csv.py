"""Create model-compatible network-flow CSV files for SecureFlow-AI testing."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import random

import joblib
import pandas as pd


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS = ROOT / "data" / "processed" / "preprocessing_artifacts.joblib"
OUTPUT = ROOT / "data" / "demo" / "network_traffic_analysis_1000.csv"


def row(source_ip: str, timestamp: str, **values: float | int | str) -> dict:
    record = {column: 0 for column in SELECTED_COLUMNS}
    record.update(
        {
            "Timestamp": timestamp,
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


def build_records(total_rows: int) -> list[dict]:
    """Create a repeatable mix of benign and clearly demonstrable attack flows."""
    scenarios = [
        (55, "10.20.10", {}),
        (15, "10.20.40", {"Destination Port": 80, "Flow Packets/s": 15_000, "Flow Bytes/s": 2_000_000}),
        (10, "10.20.50", {"Destination Port": 443, "SYN Flag Count": 35, "Flow Packets/s": 4_000}),
        (10, "172.16.30", {"Destination Port": 22, "Flow Duration": 30_000, "Total Fwd Packets": 3, "Total Backward Packets": 2}),
        (5, "172.16.40", {"Destination Port": 21, "Flow Packets/s": 800, "Flow Bytes/s": 200_000}),
        (5, "10.20.60", {"Destination Port": 8080, "Flow Bytes/s": 1_500_000, "Flow Packets/s": 500}),
    ]
    counts = [total_rows * percentage // 100 for percentage, _subnet, _values in scenarios]
    counts[0] += total_rows - sum(counts)
    start = datetime(2026, 10, 8, 10, 0, tzinfo=timezone.utc)
    randomizer = random.Random(42)
    records: list[dict] = []
    index = 0
    for (_percentage, subnet, values), count in zip(scenarios, counts):
        for number in range(count):
            timestamp = (start + timedelta(seconds=index * 3 + randomizer.randint(0, 2))).isoformat().replace("+00:00", "Z")
            source_ip = f"{subnet}.{10 + (number % 240)}"
            records.append(row(source_ip, timestamp, **values))
            index += 1
    randomizer.shuffle(records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a SecureFlow-AI network-flow CSV.")
    parser.add_argument("--rows", type=int, default=1_000, help="Number of network-flow rows to create.")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.rows < 1:
        raise SystemExit("--rows must be at least 1")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    dataframe = pd.DataFrame(build_records(args.rows))
    dataframe.to_csv(args.output, index=False)
    print(f"Created {len(dataframe):,} network-flow rows: {args.output}")


if __name__ == "__main__":
    main()
