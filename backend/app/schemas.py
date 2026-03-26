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


class VoiceResponse(BaseModel):
    transcript: str
    detected_language: str
    mode: str
    response: str


class TaxAnalyzeRequest(BaseModel):
    session_id: str
    form16_data: dict[str, Any]
    regime_preference: str = "new"


class PortfolioAnalyzeRequest(BaseModel):
    session_id: str
    holdings: list[dict[str, Any]]


class NewsQueryResponse(BaseModel):
    items: list[dict[str, Any]]
