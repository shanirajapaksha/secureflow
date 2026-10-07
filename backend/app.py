from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .detection import DetectionService
from .realtime import RealtimeService
from .routers.prediction import create_prediction_router
from .routers.realtime import create_realtime_router
from .routers.system import create_system_router
from .routers.management import create_management_router
from .persistence import Store


detector = DetectionService()
store = Store(settings.history_db_path)
realtime = RealtimeService(detector, persistence_callback=store.record_capture_and_prediction)

app = FastAPI(
    title="SecureFlow-AI Hybrid NIDS API",
    version="1.1.0",
    description="Validated CSV and real-time network-flow intrusion detection API.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.allowed_origins),
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(create_system_router(detector))
app.include_router(create_prediction_router(detector, store))
app.include_router(create_realtime_router(detector, realtime, store))
app.include_router(create_management_router(store))
