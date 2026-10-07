import io

import pandas as pd
from fastapi.testclient import TestClient

from backend.app import app, detector
from backend.detection import CICFLOWMETER_COLUMN_ALIASES, signature_detection
from backend.realtime import local_capture_interfaces, parse_interfaces


client = TestClient(app)


def valid_csv_bytes() -> bytes:
    row = {column: 0 for column in detector.selected_columns}
    row.update(
        {
            "Flow Duration": 100_000,
            "Total Fwd Packets": 10,
            "Total Backward Packets": 10,
            "Source IP": "192.0.2.1",
            "Timestamp": "2026-01-01T00:00:00Z",
        }
    )
    return pd.DataFrame([row]).to_csv(index=False).encode()


def test_health_reports_loaded_model():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True
    assert response.json()["artifacts_loaded"] is True


def test_predict_accepts_valid_cicflowmeter_csv():
    response = client.post(
        "/predict",
        files={"file": ("flows.csv", valid_csv_bytes(), "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["summary"]["total_rows"] == 1
    assert len(body["predictions"]) == 1
    assert body["predictions"][0]["Source_IP"] == "192.0.2.1"


def test_predict_rejects_wrong_extension():
    response = client.post(
        "/predict",
        files={"file": ("flows.txt", b"a,b\n1,2", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload a CSV file."


def test_predict_rejects_incompatible_schema():
    response = client.post(
        "/predict",
        files={"file": ("flows.csv", b"foo,bar\n1,2", "text/csv")},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["message"].startswith("CSV does not match")
    assert detail["matched_features"] == 0


def test_signature_rule_detects_syn_flood():
    status, reason = signature_detection(pd.Series({"SYN Flag Count": 21, "Flow Duration": 100_000}))

    assert status == "INTRUSION"
    assert "SYN flood" in reason


def test_realtime_status_is_available_without_capture_tools():
    response = client.get("/realtime/status")

    assert response.status_code == 200
    assert response.json()["running"] is False


def test_cicflowmeter_v4_column_aliases_match_model_schema():
    reverse_aliases = {target: source for source, target in CICFLOWMETER_COLUMN_ALIASES.items()}
    row = {reverse_aliases.get(column, column): 0 for column in detector.selected_columns}
    normalized = detector.validate_dataframe(pd.DataFrame([row]))

    assert set(detector.selected_columns).issubset(normalized.columns)


def test_tshark_interface_output_is_parsed():
    interfaces = parse_interfaces("1. Ethernet\n4. Wi-Fi\ninvalid line")

    assert interfaces == [
        {"id": "1", "name": "Ethernet", "raw": "1. Ethernet"},
        {"id": "4", "name": "Wi-Fi", "raw": "4. Wi-Fi"},
    ]


def test_windows_local_interface_filter_excludes_extcap():
    output = "4. \\Device\\NPF_ABC (Wi-Fi)\n14. wifidump (Wi-Fi remote capture)"

    assert local_capture_interfaces(output, platform_name="nt") == [
        {"id": "4", "name": "\\Device\\NPF_ABC (Wi-Fi)", "raw": "4. \\Device\\NPF_ABC (Wi-Fi)"}
    ]
