# [DEV1] schemas.py — Pydantic models. Dev2: append your schemas at the bottom.
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SessionStartResponse(BaseModel):
    session_id: str


class UserProfileUpdateRequest(BaseModel):
    session_id: str
    age: int | None = None
    income: float | None = None
    expenses: float | None = None
    investments: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    risk_profile: str | None = None


class UserProfileResponse(BaseModel):
    session_id: str
    created_at: datetime
    last_active: datetime
    profile: dict[str, Any]


class VoiceRequest(BaseModel):
    session_id: str
    text: str | None = None
    language: str | None = None
    mode: str = "agent"
    use_tts: bool = False


class VoiceResponse(BaseModel):
    transcript: str
    detected_language: str
    mode: str
    response: str
    tts_requested: bool = False
    tts_enabled: bool = False
    tts_skipped_reason: str | None = None
    tts_audio_base64: str | None = None
    tts_content_type: str | None = None


class VoiceCommandOption(BaseModel):
    id: str
    description: str
    examples: list[str] = Field(default_factory=list)


class VoiceCommandResolveRequest(BaseModel):
    session_id: str
    transcript: str
    commands: list[VoiceCommandOption]


class VoiceCommandResolveResponse(BaseModel):
    command_id: str
    confidence: float = 0.0
    reason: str | None = None


class TaxAnalyzeRequest(BaseModel):
    session_id: str
    form16_data: dict[str, Any]
    regime_preference: str = "new"


class PortfolioAnalyzeRequest(BaseModel):
    session_id: str
    holdings: list[dict[str, Any]]


class NewsQueryResponse(BaseModel):
    items: list[dict[str, Any]]
