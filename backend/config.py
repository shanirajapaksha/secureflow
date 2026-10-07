from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - only used during a broken installation
    load_dotenv = None


BASE_DIR = Path(__file__).resolve().parent.parent

if load_dotenv:
    load_dotenv(BASE_DIR / ".env")
    load_dotenv(BASE_DIR / "backend" / ".env", override=True)


def _as_int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except ValueError:
        return default


def _as_float(name: str, default: float) -> float:
    try:
        return float(os.getenv(name, str(default)))
    except ValueError:
        return default


def _origins() -> list[str]:
    value = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:8080,http://127.0.0.1:8080",
    )
    return [origin.strip() for origin in value.split(",") if origin.strip()]


@dataclass(frozen=True)
class Settings:
    base_dir: Path = BASE_DIR
    model_path: Path = BASE_DIR / "models" / "best_nids_model.joblib"
    artifacts_path: Path = BASE_DIR / "data" / "processed" / "preprocessing_artifacts.joblib"
    live_dir: Path = BASE_DIR / "data" / "live"
    allowed_origins: tuple[str, ...] = tuple(_origins())
    max_upload_bytes: int = _as_int("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)
    max_csv_rows: int = _as_int("MAX_CSV_ROWS", 100_000)
    min_feature_coverage: float = _as_float("MIN_FEATURE_COVERAGE", 0.80)
    max_recent_alerts: int = _as_int("MAX_RECENT_ALERTS", 500)
    converter_timeout_seconds: int = _as_int("CONVERTER_TIMEOUT_SECONDS", 180)
    history_db_path: Path = BASE_DIR / "data" / "history.db"


settings = Settings()
settings.live_dir.mkdir(parents=True, exist_ok=True)
