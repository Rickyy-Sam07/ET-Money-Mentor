import json
import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Portfolio, Profile, TaxData, User
from app.schemas import (
    PortfolioAnalyzeRequest,
    SessionStartResponse,
    TaxAnalyzeRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
    VoiceRequest,
    VoiceResponse,
)
from app.services.news_service import query_news
from app.services.portfolio_service import analyze_portfolio
from app.services.tax_service import analyze_tax
from app.services.upload_service import parse_uploaded_file
from app.services.voice_service import detect_language, respond

router = APIRouter(prefix="/api", tags=["api"])

voice_turns: dict[str, int] = {}
PROHIBITED_PHRASES = ("guaranteed return", "guaranteed returns")


def _sanitize_text(text: str) -> str:
    sanitized = text
    for phrase in PROHIBITED_PHRASES:
        sanitized = sanitized.replace(phrase, "potential outcome")
        sanitized = sanitized.replace(phrase.title(), "Potential outcome")
        sanitized = sanitized.replace(phrase.upper(), "POTENTIAL OUTCOME")
    return sanitized


def _sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, str):
        return _sanitize_text(payload)
    if isinstance(payload, list):
        return [_sanitize_payload(item) for item in payload]
    if isinstance(payload, dict):
        return {k: _sanitize_payload(v) for k, v in payload.items()}
    return payload


def _get_user_by_session(db: Session, session_id: str) -> User:
    user = db.query(User).filter(User.session_id == session_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Session not found")
    user.last_active = datetime.utcnow()
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/session/start", response_model=SessionStartResponse)
def session_start(db: Session = Depends(get_db)) -> SessionStartResponse:
    session_id = str(uuid.uuid4())
    user = User(session_id=session_id)
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()

    return SessionStartResponse(session_id=session_id)


@router.get("/user", response_model=UserProfileResponse)
def get_user(session_id: str, db: Session = Depends(get_db)) -> UserProfileResponse:
    user = _get_user_by_session(db, session_id)
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    return UserProfileResponse(
        session_id=user.session_id,
        created_at=user.created_at,
        last_active=user.last_active,
        profile={
            "age": profile.age if profile else None,
            "income": profile.income if profile else None,
            "expenses": profile.expenses if profile else None,
            "investments": json.loads(profile.investments) if profile and profile.investments else [],
            "goals": json.loads(profile.goals) if profile and profile.goals else [],
            "risk_profile": profile.risk_profile if profile else None,
        },
    )


@router.post("/user/update")
def update_user(payload: UserProfileUpdateRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)

    profile.age = payload.age
    profile.income = payload.income
    profile.expenses = payload.expenses
    profile.investments = json.dumps(payload.investments)
    profile.goals = json.dumps(payload.goals)
    profile.risk_profile = payload.risk_profile

    db.add(profile)
    db.commit()

    return {"message": "Profile updated"}


@router.post("/voice/process", response_model=VoiceResponse)
def process_voice(payload: VoiceRequest, db: Session = Depends(get_db)) -> VoiceResponse:
    _get_user_by_session(db, payload.session_id)

    transcript = payload.text or ""
    detected_language = payload.language or detect_language(transcript)
    turn = voice_turns.get(payload.session_id, 0)
    reply = _sanitize_text(respond(payload.mode, transcript, turn))
    voice_turns[payload.session_id] = turn + 1

    return VoiceResponse(
        transcript=transcript,
        detected_language=detected_language,
        mode=payload.mode,
        response=reply,
    )


@router.post("/upload")
async def upload_file(session_id: str, file: UploadFile = File(...), db: Session = Depends(get_db)) -> dict:
    _get_user_by_session(db, session_id)

    content = await file.read()
    parsed = _sanitize_payload(parse_uploaded_file(file.filename, content))
    return {"filename": file.filename, "parsed": parsed}


@router.post("/tax/analyze")
def tax_analyze(payload: TaxAnalyzeRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    result = _sanitize_payload(analyze_tax(payload.form16_data, payload.regime_preference))

    row = TaxData(
        user_id=user.id,
        form16_data=json.dumps(payload.form16_data),
        deductions=json.dumps(result["deductions"]),
        regime_choice=result["regime_comparison"]["selected"],
    )
    db.add(row)
    db.commit()

    return result


@router.post("/portfolio/analyze")
def portfolio_analyze(payload: PortfolioAnalyzeRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    result = _sanitize_payload(analyze_portfolio(payload.holdings))

    metrics = result["metrics"]
    row = Portfolio(
        user_id=user.id,
        holdings=json.dumps(payload.holdings),
        xirr=metrics["xirr"],
        overlap=metrics["overlap_percent"],
        expense_ratio=metrics["expense_ratio_drag"],
        benchmark=json.dumps(metrics["benchmark"]),
    )
    db.add(row)
    db.commit()

    return result


@router.get("/news/query")
def news_query(session_id: str, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, session_id)
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()

    context = {
        "holdings": json.loads(profile.investments) if profile and profile.investments else [],
        "goals": json.loads(profile.goals) if profile and profile.goals else [],
        "risk_profile": profile.risk_profile if profile else None,
    }
    items = _sanitize_payload(query_news(context))
    return {"items": items}
