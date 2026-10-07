import io

from fastapi import HTTPException, UploadFile
import pandas as pd

from .config import settings


async def read_csv_upload_with_content(file: UploadFile) -> tuple[pd.DataFrame, bytes]:
    filename = file.filename or ""
    if not filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a CSV file.")

    content = bytearray()
    while chunk := await file.read(1024 * 1024):
        content.extend(chunk)
        if len(content) > settings.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"CSV exceeds the {settings.max_upload_bytes // (1024 * 1024)} MB upload limit.",
            )

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded CSV is empty.")

    try:
        return pd.read_csv(io.BytesIO(content)), bytes(content)
    except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid CSV file: {exc}") from exc


async def read_csv_upload(file: UploadFile) -> pd.DataFrame:
    dataframe, _content = await read_csv_upload_with_content(file)
    return dataframe
