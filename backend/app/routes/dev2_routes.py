"""Dev2 API routes – Onboarding, Life Event, Couple, What-if, Emergency, Recommendations."""

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import (
    CoupleData,
    EmergencyInteraction,
    FinancialGoal,
    LifeEvent,
    Profile,
    Recommendation,
    User,
)
from app.schemas import (
    CoupleOptimizeRequest,
    EmergencyRequest,
    LifeEventRequest,
    OnboardingSubmitRequest,
    WhatIfRequest,
)
from app.services.couple_service import optimize_couple
from app.services.emergency_service import respond_emergency
from app.services.life_event_service import advise_life_event
from app.services.onboarding_service import compute_fire_roadmap, compute_health_score
from app.services.recommendations_service import get_recommendations
from app.services.whatif_service import simulate_whatif

router = APIRouter(prefix="/api", tags=["dev2"])

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


def _get_profile_dict(db: Session, user_id: int) -> dict[str, Any]:
    profile = db.query(Profile).filter(Profile.user_id == user_id).first()
    if not profile:
        return {}
    return {
        "age": profile.age or 30,
        "income": profile.income or 0,
        "expenses": profile.expenses or 0,
        "investments": json.loads(profile.investments) if profile.investments else [],
        "goals": json.loads(profile.goals) if profile.goals else [],
        "risk_profile": profile.risk_profile or "moderate",
    }


# ── Onboarding ───────────────────────────────────────────────


@router.post("/onboarding/submit")
def onboarding_submit(payload: OnboardingSubmitRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)

    # Update profile
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        profile = Profile(user_id=user.id)
    profile.age = payload.age
    profile.income = payload.income
    profile.expenses = payload.expenses
    profile.investments = json.dumps([inv.copy() for inv in payload.investments])
    profile.goals = json.dumps([g.copy() for g in payload.goals])
    profile.risk_profile = payload.risk_profile
    db.add(profile)
    db.commit()

    # Compute health score
    health_score = compute_health_score(
        age=payload.age,
        income=payload.income,
        expenses=payload.expenses,
        investments=payload.investments,
        emergency_fund=payload.emergency_fund,
        health_insurance=payload.health_insurance,
        life_insurance=payload.life_insurance,
        debt_emi=payload.debt_emi,
    )

    # Generate FIRE roadmap
    roadmap = compute_fire_roadmap(
        age=payload.age,
        income=payload.income,
        expenses=payload.expenses,
        investments=payload.investments,
        goals=payload.goals,
        risk_profile=payload.risk_profile,
        emergency_fund=payload.emergency_fund,
        health_insurance=payload.health_insurance,
        debt_emi=payload.debt_emi,
    )

    # Store in DB
    goal = FinancialGoal(
        user_id=user.id,
        goal_type="fire_roadmap",
        target_amount=payload.income * 25,
        monthly_sip=roadmap[0]["sip_amount"] if roadmap else 0,
        timeline_months=len(roadmap),
        roadmap=json.dumps(roadmap),
        health_score=json.dumps(health_score),
    )
    db.add(goal)
    db.commit()

    return _sanitize_payload({
        "health_score": health_score,
        "roadmap": roadmap,
        "message": "Onboarding complete. Your Money Health Score and FIRE roadmap are ready.",
    })


# ── Life Event ───────────────────────────────────────────────


@router.post("/life-event/advise")
def life_event_advise(payload: LifeEventRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = advise_life_event(payload.event_type, payload.amount, profile_dict)

    row = LifeEvent(
        user_id=user.id,
        event_type=payload.event_type,
        amount=payload.amount,
        advice=json.dumps(result),
    )
    db.add(row)
    db.commit()

    return _sanitize_payload(result)


# ── Couple's Planner ─────────────────────────────────────────


@router.post("/couple/optimize")
def couple_optimize(payload: CoupleOptimizeRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)

    result = optimize_couple(payload.partner1, payload.partner2)

    row = CoupleData(
        user_id=user.id,
        partner2_profile=json.dumps(payload.partner2),
        joint_plan=json.dumps(result),
    )
    db.add(row)
    db.commit()

    return _sanitize_payload(result)


# ── What-if Simulation ───────────────────────────────────────


@router.post("/whatif/simulate")
def whatif_simulate(payload: WhatIfRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = simulate_whatif(payload.scenario, payload.amount, profile_dict)
    return _sanitize_payload(result)


# ── Emergency Chatbot ────────────────────────────────────────


@router.post("/emergency/respond")
def emergency_respond(payload: EmergencyRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = respond_emergency(payload.crisis_type, payload.details, profile_dict)

    row = EmergencyInteraction(
        user_id=user.id,
        crisis_type=payload.crisis_type,
        details=payload.details,
        steps=json.dumps(result["action_steps"]),
    )
    db.add(row)
    db.commit()

    return _sanitize_payload(result)


# ── Recommendations ──────────────────────────────────────────


@router.get("/recommendations")
def recommendations(session_id: str, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = get_recommendations(profile_dict)

    row = Recommendation(
        user_id=user.id,
        category=result["segment"],
        items=json.dumps(result["recommended_funds"]),
    )
    db.add(row)
    db.commit()

    return _sanitize_payload(result)
