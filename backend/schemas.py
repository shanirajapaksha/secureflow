from typing import Optional

from pydantic import BaseModel, Field


class RealtimeStartRequest(BaseModel):
    interface: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="TShark interface number or name.",
    )
    duration_seconds: Optional[int] = Field(default=None, ge=1, le=3600)
    window_seconds: int = Field(
        default=5,
        ge=2,
        le=60,
        description="Analysis window size for continuous monitoring.",
    )


class CaptureAnalyzeRequest(BaseModel):
    interface: str = Field(..., min_length=1, max_length=300)
    duration_seconds: int = Field(default=10, ge=1, le=300)


class ProcessCaptureRequest(BaseModel):
    capture_file: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Capture inside data/live. Uses the latest capture when omitted.",
    )
