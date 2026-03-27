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


# ── Dev2 schemas ─────────────────────────────────────────────


class OnboardingSubmitRequest(BaseModel):
    session_id: str
    age: int
    income: float
    expenses: float
    investments: list[dict[str, Any]] = Field(default_factory=list)
    goals: list[dict[str, Any]] = Field(default_factory=list)
    risk_profile: str = "moderate"
    emergency_fund: float = 0
    health_insurance: float = 0
    life_insurance: float = 0
    debt_emi: float = 0


class LifeEventRequest(BaseModel):
    session_id: str
    event_type: str  # bonus | inheritance | marriage | new_baby
    amount: float = 0
    timing: str = "now"


class CoupleOptimizeRequest(BaseModel):
    session_id: str
    partner1: dict[str, Any]
    partner2: dict[str, Any]


class WhatIfRequest(BaseModel):
    session_id: str
    scenario: str
    amount: float = 0


class EmergencyRequest(BaseModel):
    session_id: str
    crisis_type: str  # job_loss | medical | debt_crisis | market_crash
    details: str = ""
