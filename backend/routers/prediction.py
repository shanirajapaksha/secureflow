from fastapi import APIRouter, File, HTTPException, UploadFile

from ..detection import DetectionService, InputValidationError
from ..uploads import read_csv_upload_with_content
from ..persistence import Store


def validation_error(exc: InputValidationError) -> HTTPException:
    return HTTPException(status_code=422, detail={"message": str(exc), **exc.details})


def create_prediction_router(detector: DetectionService, store: Store | None = None) -> APIRouter:
    router = APIRouter(tags=["prediction"])

    @router.post("/predict")
    async def predict(file: UploadFile = File(...)):
        dataframe, content = await read_csv_upload_with_content(file)
        try:
            response = detector.predict(dataframe)
            if store:
                store.record_upload_and_prediction(file.filename or "uploaded.csv", content, response)
            return response
        except InputValidationError as exc:
            raise validation_error(exc) from exc

    return router
