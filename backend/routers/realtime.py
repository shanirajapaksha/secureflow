from fastapi import APIRouter, File, UploadFile

from ..detection import DetectionService, InputValidationError
from ..realtime import RealtimeService
from ..schemas import CaptureAnalyzeRequest, ProcessCaptureRequest, RealtimeStartRequest
from ..uploads import read_csv_upload_with_content
from ..persistence import Store
from .prediction import validation_error


def create_realtime_router(detector: DetectionService, realtime: RealtimeService, store: Store | None = None) -> APIRouter:
    router = APIRouter(prefix="/realtime", tags=["realtime"])

    @router.get("/converter/status")
    def converter_status():
        return realtime.converter_status()

    @router.get("/interfaces")
    def interfaces():
        return realtime.interfaces()

    @router.post("/start")
    def start(request: RealtimeStartRequest):
        return realtime.start(request.interface, request.duration_seconds, request.window_seconds)

    @router.post("/stop")
    def stop():
        return realtime.stop()

    @router.get("/status")
    def status():
        return realtime.serialize()

    @router.get("/alerts")
    def alerts(limit: int = 100):
        return realtime.alerts(limit)

    @router.post("/process-capture")
    def process_capture(request: ProcessCaptureRequest):
        try:
            return realtime.process_capture(request.capture_file)
        except InputValidationError as exc:
            raise validation_error(exc) from exc

    @router.post("/capture-and-analyze")
    def capture_and_analyze(request: CaptureAnalyzeRequest):
        try:
            return realtime.capture_and_analyze(request.interface, request.duration_seconds)
        except InputValidationError as exc:
            raise validation_error(exc) from exc

    @router.post("/ingest-flow-csv")
    async def ingest_flow_csv(file: UploadFile = File(...)):
        dataframe, content = await read_csv_upload_with_content(file)
        try:
            response = detector.predict(dataframe)
        except InputValidationError as exc:
            raise validation_error(exc) from exc
        realtime.remember(response["predictions"])
        if store:
            store.record_upload_and_prediction(file.filename or "flow-upload.csv", content, response)
        return response

    return router
