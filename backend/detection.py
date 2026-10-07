from datetime import datetime, timezone
from typing import Any

import joblib
import numpy as np
import pandas as pd

from .config import Settings, settings


LABEL_COLUMNS = {"label", "class", "category", "attack"}

# CICFlowMeter V4 renamed a few CICIDS2017 columns. Normalize both formats to
# the exact feature names used when this model was trained.
CICFLOWMETER_COLUMN_ALIASES = {
    "Dst Port": "Destination Port",
    "Total Fwd Packet": "Total Fwd Packets",
    "Total Bwd packets": "Total Backward Packets",
    "Total Length of Fwd Packet": "Total Length of Fwd Packets",
    "Total Length of Bwd Packet": "Total Length of Bwd Packets",
    "Packet Length Min": "Min Packet Length",
    "FWD Init Win Bytes": "Init_Win_bytes_forward",
    "Bwd Init Win Bytes": "Init_Win_bytes_backward",
    "Fwd Act Data Pkts": "act_data_pkt_fwd",
    "Fwd Seg Size Min": "min_seg_size_forward",
}


class InputValidationError(ValueError):
    """Raised when an uploaded dataframe cannot safely be classified."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.details = details or {}


class DetectionService:
    def __init__(self, app_settings: Settings = settings):
        self.settings = app_settings
        if not app_settings.model_path.exists():
            raise FileNotFoundError(f"Model not found: {app_settings.model_path}")
        if not app_settings.artifacts_path.exists():
            raise FileNotFoundError(f"Artifacts not found: {app_settings.artifacts_path}")

        self.model = joblib.load(app_settings.model_path)
        artifacts = joblib.load(app_settings.artifacts_path)
        self.scaler = artifacts["scaler"]
        self.label_encoder = artifacts["label_encoder"]
        self.selected_columns = list(artifacts["selected_columns"])
        self.corr_drop = artifacts.get("corr_drop", [])
        self.zero_var_cols = artifacts.get("zero_var_cols", [])
        self.train_means = artifacts.get("train_means")

    @property
    def model_name(self) -> str:
        return type(self.model).__name__

    def validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            raise InputValidationError("Uploaded CSV is empty.")
        if len(df) > self.settings.max_csv_rows:
            raise InputValidationError(
                f"CSV has {len(df):,} rows; the maximum is {self.settings.max_csv_rows:,}.",
                {"row_count": len(df), "max_rows": self.settings.max_csv_rows},
            )

        normalized = df.copy()
        normalized.columns = normalized.columns.astype(str).str.strip().str.replace("\ufeff", "", regex=False)
        normalized = normalized.rename(columns=CICFLOWMETER_COLUMN_ALIASES)
        duplicates = normalized.columns[normalized.columns.duplicated()].tolist()
        if duplicates:
            raise InputValidationError(
                "CSV contains duplicate column names.",
                {"duplicate_columns": sorted(set(duplicates))},
            )

        supplied = set(normalized.columns)
        matched = [column for column in self.selected_columns if column in supplied]
        coverage = len(matched) / len(self.selected_columns)
        if coverage < self.settings.min_feature_coverage:
            missing = [column for column in self.selected_columns if column not in supplied]
            raise InputValidationError(
                "CSV does not match the CICIDS2017/CICFlowMeter feature schema.",
                {
                    "matched_features": len(matched),
                    "required_features": len(self.selected_columns),
                    "coverage": round(coverage, 3),
                    "minimum_coverage": self.settings.min_feature_coverage,
                    "missing_features": missing,
                },
            )
        return normalized

    def preprocess(self, df: pd.DataFrame) -> np.ndarray:
        features = df.copy()
        label = next((col for col in features.columns if col.lower() in LABEL_COLUMNS), None)
        if label:
            features = features.drop(columns=[label])

        categorical = features.select_dtypes(include=["object", "string", "category"]).columns
        if len(categorical):
            features = pd.get_dummies(features, columns=categorical, drop_first=False)

        features = features.drop(columns=[c for c in self.zero_var_cols if c in features], errors="ignore")
        features = features.drop(columns=[c for c in self.corr_drop if c in features], errors="ignore")
        for column in self.selected_columns:
            if column not in features:
                features[column] = 0

        features = features.reindex(columns=self.selected_columns)
        features = features.apply(pd.to_numeric, errors="coerce")
        features = features.replace([np.inf, -np.inf], np.nan)
        features = features.fillna(self.train_means if self.train_means is not None else 0)
        return self.scaler.transform(features)

    def predict(self, input_df: pd.DataFrame) -> dict[str, Any]:
        df = self.validate_dataframe(input_df)
        label_column = next((col for col in df.columns if col.lower() in LABEL_COLUMNS), None)
        truth = df[label_column].astype(str).str.strip() if label_column else None
        matrix = self.preprocess(df)

        encoded = self.model.predict(matrix)
        ml_labels = self.label_encoder.inverse_transform(encoded)
        predictions = []

        for index, (_, row) in enumerate(df.iterrows()):
            signature_status, signature_reason = signature_detection(row)
            if signature_status == "INTRUSION":
                label = "Signature_Detected_Attack"
                status = "INTRUSION"
                method = "Signature-Based"
                reason = signature_reason
            else:
                label = str(ml_labels[index]).strip()
                status = "BENIGN" if label.upper() == "BENIGN" else "INTRUSION"
                method = "Anomaly-Based"
                reason = "No signature match; predicted by ML model"

            predictions.append(
                {
                    "Alert_ID": index + 1,
                    "Timestamp": get_timestamp_value(row),
                    "Source_IP": get_source_ip(row),
                    "Detection_Method": method,
                    "Predicted_Intrusion_Type": label,
                    "Traffic_Status": status,
                    "Reason": reason,
                    "Severity": get_severity(label),
                }
            )

        result_df = pd.DataFrame(predictions)
        evaluation = None
        known_labels = set(map(str, self.label_encoder.classes_))
        if truth is not None and truth.isin(known_labels).all():
            from sklearn.metrics import accuracy_score

            evaluation = {
                "label_column": label_column,
                "accuracy": float(accuracy_score(truth, result_df["Predicted_Intrusion_Type"])),
            }

        return {
            "summary": {
                "total_rows": len(result_df),
                "benign_count": int((result_df["Traffic_Status"] == "BENIGN").sum()),
                "intrusion_count": int((result_df["Traffic_Status"] == "INTRUSION").sum()),
                "signature_count": int((result_df["Detection_Method"] == "Signature-Based").sum()),
                "anomaly_count": int((result_df["Detection_Method"] == "Anomaly-Based").sum()),
            },
            "evaluation": evaluation,
            "predictions": predictions,
        }


def signature_detection(row: pd.Series) -> tuple[str, str]:
    def value(column: str, default: float = 0) -> float:
        raw = row.get(column, default)
        try:
            return default if pd.isna(raw) else float(raw)
        except (TypeError, ValueError):
            return default

    alerts = []
    if value("Destination Port") in (80, 443) and value("Flow Packets/s") > 10_000:
        alerts.append("Possible DoS/DDoS pattern detected")
    if value("SYN Flag Count") > 20:
        alerts.append("Possible SYN flood detected")
    if value("Flow Duration") < 50_000 and value("Total Fwd Packets") < 5 and value("Total Backward Packets") < 5:
        alerts.append("Possible port scanning activity")
    if value("Flow Bytes/s") > 1_000_000:
        alerts.append("Suspiciously high byte rate")
    if value("Destination Port") == 21 and value("Flow Packets/s") > 500:
        alerts.append("Possible FTP brute-force activity")
    return ("INTRUSION", "; ".join(alerts)) if alerts else ("BENIGN", "No signature rule matched")


def get_source_ip(row: pd.Series) -> str:
    for column in ("Source_IP", "Source IP", "Src IP", "src_ip", "source_ip"):
        if column in row.index and pd.notna(row[column]):
            return str(row[column])
    return "N/A"


def get_timestamp_value(row: pd.Series) -> str | None:
    for column in ("Timestamp", "timestamp", "Time", "time"):
        if column in row.index and pd.notna(row[column]):
            return str(row[column])
    return None


def get_severity(label: str) -> str:
    if any(value in str(label) for value in ("DDoS", "DoS", "Heartbleed", "Infiltration", "Bot")):
        return "High"
    if any(value in str(label) for value in ("PortScan", "Web Attack", "Brute", "FTP", "Signature_Detected_Attack")):
        return "Medium"
    return "Low" if str(label).upper() == "BENIGN" else "Review"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
