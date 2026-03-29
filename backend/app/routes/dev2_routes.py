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
from app.services.llm_client import generate_explanation, generate_emergency_response
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

    # AI explanation
    ai_summary = generate_explanation(
        f"A {payload.age}-year-old with annual income ₹{payload.income:,}, "
        f"monthly expenses ₹{payload.expenses:,}, "
        f"emergency fund ₹{payload.emergency_fund:,}, "
        f"risk profile: {payload.risk_profile}. "
        f"Money Health Score: {health_score['overall']}/100. "
        f"Dimensions: {json.dumps(health_score)}. "
        f"Monthly SIP recommended: ₹{roadmap[0]['sip_amount'] if roadmap else 0:,}. "
        "Summarise their financial health and the top 2-3 action items from the roadmap.",
        fallback="Onboarding complete. Your Money Health Score and FIRE roadmap are ready.",
    )

    return _sanitize_payload({
        "health_score": health_score,
        "roadmap": roadmap,
        "ai_summary": ai_summary,
        "message": "Onboarding complete. Your Money Health Score and FIRE roadmap are ready.",
    })


# ── Life Event ───────────────────────────────────────────────


@router.post("/life-event/advise")
def life_event_advise(payload: LifeEventRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = advise_life_event(payload.event_type, payload.amount, profile_dict)

    # AI explanation
    ai_advice = generate_explanation(
        f"User has a life event: {payload.event_type}, amount: ₹{payload.amount:,}. "
        f"Profile: age {profile_dict.get('age')}, income ₹{profile_dict.get('income', 0):,}. "
        f"Suggested allocations: {json.dumps(result['allocations'])}. "
        "Give a personalised 3-sentence recommendation for this life event.",
        fallback=result.get("explanation", ""),
    )
    result["ai_advice"] = ai_advice

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

    # AI explanation
    ai_plan = generate_explanation(
        f"Couple financial plan: Partner 1 income ₹{payload.partner1.get('income', 0):,}, "
        f"Partner 2 income ₹{payload.partner2.get('income', 0):,}. "
        f"HRA tax saved: ₹{result['hra_optimization']['tax_saved']:,}. "
        f"NPS additional tax saved: ₹{result['nps_matching']['combined_tax_saved']:,}. "
        "Summarise the joint optimisation plan in 3 sentences.",
        fallback=result.get("explanation", ""),
    )
    result["ai_plan"] = ai_plan

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

    # AI narration
    scenarios_summary = "; ".join(
        f"{s['name']}: 5yr ₹{s['projected_5y']:,}, 10yr ₹{s['projected_10y']:,}"
        for s in result["scenarios"]
    )
    ai_narration = generate_explanation(
        f"What-if scenario: '{payload.scenario}', amount ₹{payload.amount:,}. "
        f"Baseline 5yr: ₹{result['base_projection']['year_5']:,}. "
        f"Scenarios: {scenarios_summary}. "
        "Which scenario is best for this user and why? Keep it to 3 sentences.",
        fallback=result.get("recommendation", ""),
    )
    result["ai_narration"] = ai_narration

    return _sanitize_payload(result)


# ── Emergency Chatbot ────────────────────────────────────────


@router.post("/emergency/respond")
def emergency_respond(payload: EmergencyRequest, db: Session = Depends(get_db)) -> dict:
    user = _get_user_by_session(db, payload.session_id)
    profile_dict = _get_profile_dict(db, user.id)

    result = respond_emergency(payload.crisis_type, payload.details, profile_dict)

    # AI empathetic response
    profile_summary = (
        f"Age: {profile_dict.get('age', 'unknown')}, "
        f"Income: ₹{profile_dict.get('income', 0):,}, "
        f"Emergency fund covers ~{result.get('emergency_fund_months', 0)} months"
    )
    ai_response = generate_emergency_response(
        payload.crisis_type,
        payload.details,
        profile_summary,
        fallback=result.get("empathy_message", ""),
    )
    result["ai_response"] = ai_response

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

    # AI explanation
    fund_names = ", ".join(f["name"] for f in result["recommended_funds"][:3])
    ai_why = generate_explanation(
        f"User segment: {result['segment']}, risk: {result['risk_profile']}. "
        f"Recommended funds: {fund_names}. "
        f"Asset allocation: {json.dumps(result['asset_allocation'])}. "
        "Explain in 3 sentences why these funds and allocation fit this user.",
        fallback=result.get("explanation", ""),
    )
    result["ai_explanation"] = ai_why

    row = Recommendation(
        user_id=user.id,
        category=result["segment"],
        items=json.dumps(result["recommended_funds"]),
    )
    db.add(row)
    db.commit()

    return _sanitize_payload(result)
