from fastapi import APIRouter

from ..config import settings
from ..detection import DetectionService


def create_system_router(detector: DetectionService) -> APIRouter:
    router = APIRouter(tags=["system"])

    @router.get("/")
    def home():
        return {"message": "Hybrid NIDS API is running"}

    @router.get("/health")
    def health():
        return {
            "status": "ok",
            "model_loaded": detector.model is not None,
            "artifacts_loaded": detector.scaler is not None,
            "model_type": detector.model_name,
            "max_upload_bytes": settings.max_upload_bytes,
            "max_csv_rows": settings.max_csv_rows,
        }

    return router
