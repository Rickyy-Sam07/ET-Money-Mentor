"""Onboarding service – Money Health Score (6 dimensions) + FIRE roadmap."""

from typing import Any
import math


def _score_emergency(emergency_fund: float, monthly_expenses: float) -> int:
    """Score 0-100 based on months of expenses covered."""
    if monthly_expenses <= 0:
        return 50
    months = emergency_fund / monthly_expenses
    return min(int(months / 6 * 100), 100)


def _score_insurance(health: float, life: float, income: float) -> int:
    health_ok = 1 if health >= 500000 else health / 500000
    life_ok = 1 if income <= 0 else min(life / (income * 10), 1)
    return int(((health_ok + life_ok) / 2) * 100)


def _score_diversification(investments: list[dict[str, Any]]) -> int:
    if not investments:
        return 0
    categories = {inv.get("type", "unknown") for inv in investments}
    return min(len(categories) * 25, 100)


def _score_debt(debt_emi: float, income: float) -> int:
    if income <= 0:
        return 50
    dti = debt_emi / income
    if dti <= 0.2:
        return 100
    if dti <= 0.4:
        return 70
    if dti <= 0.6:
        return 40
    return 10


def _score_tax(income: float, investments: list[dict[str, Any]]) -> int:
    total_80c = sum(
        inv.get("amount", 0) for inv in investments
        if inv.get("type") in ("ELSS", "PPF", "NPS", "EPF", "LIC")
    )
    utilised = min(total_80c / 150000, 1)
    return int(utilised * 100)


def _score_retirement(age: int, income: float, investments: list[dict[str, Any]]) -> int:
    if age <= 0 or income <= 0:
        return 50
    years_left = max(60 - age, 1)
    total_invested = sum(inv.get("amount", 0) for inv in investments)
    # simplified: should have at least 15x annual income by 60
    target = income * 15
    # project current at 12% rough
    projected = total_invested * ((1.12) ** years_left)
    return min(int(projected / target * 100), 100)


def compute_health_score(
    age: int,
    income: float,
    expenses: float,
    investments: list[dict[str, Any]],
    emergency_fund: float,
    health_insurance: float,
    life_insurance: float,
    debt_emi: float,
) -> dict[str, Any]:
    scores = {
        "emergency_preparedness": _score_emergency(emergency_fund, expenses),
        "insurance_coverage": _score_insurance(health_insurance, life_insurance, income),
        "investment_diversification": _score_diversification(investments),
        "debt_health": _score_debt(debt_emi, income),
        "tax_efficiency": _score_tax(income, investments),
        "retirement_readiness": _score_retirement(age, income, investments),
    }
    scores["overall"] = int(sum(scores.values()) / 6)
    return scores


def compute_fire_roadmap(
    age: int,
    income: float,
    expenses: float,
    investments: list[dict[str, Any]],
    goals: list[dict[str, Any]],
    risk_profile: str,
    emergency_fund: float,
    health_insurance: float,
    debt_emi: float,
) -> list[dict[str, Any]]:
    """Generate a simplified 12-month roadmap."""

    roadmap: list[dict[str, Any]] = []
    monthly_surplus = max(income / 12 - expenses, 0)
    target_emergency = expenses * 6

    # allocation weights by risk
    alloc = {
        "conservative": {"equity": 0.3, "debt": 0.5, "gold": 0.1, "cash": 0.1},
        "moderate": {"equity": 0.5, "debt": 0.3, "gold": 0.1, "cash": 0.1},
        "aggressive": {"equity": 0.7, "debt": 0.15, "gold": 0.1, "cash": 0.05},
    }.get(risk_profile, {"equity": 0.5, "debt": 0.3, "gold": 0.1, "cash": 0.1})

    for month in range(1, 13):
        entry: dict[str, Any] = {"month": month, "actions": [], "sip_amount": 0, "allocation": dict(alloc)}

        # First priority: build emergency fund
        if emergency_fund < target_emergency and month <= 3:
            top_up = min(monthly_surplus * 0.4, target_emergency - emergency_fund)
            entry["actions"].append(
                f"Top-up emergency fund by ₹{int(top_up):,} (target: ₹{int(target_emergency):,})"
            )
            emergency_fund += top_up
            remaining = monthly_surplus - top_up
        else:
            remaining = monthly_surplus

        # Health insurance check
        if health_insurance < 500000 and month == 1:
            entry["actions"].append(
                "Get health insurance cover of at least ₹5,00,000 for self + family."
            )

        # Debt check
        if debt_emi > income * 0.4 / 12 and month == 1:
            entry["actions"].append(
                "Consider prepaying high-cost debt to bring EMI below 40% of monthly income."
            )

        # SIP allocation
        sip = max(int(remaining * 0.8), 0)
        entry["sip_amount"] = sip
        if sip > 0:
            entry["actions"].append(
                f"Invest ₹{sip:,}/month via SIP: "
                + ", ".join(f"{k.title()} {int(v*100)}%" for k, v in alloc.items())
            )

        # Tax-saving reminder
        if month in (1, 6):
            entry["actions"].append(
                "Review 80C investments (ELSS/PPF/NPS). Max deduction: ₹1,50,000."
            )

        roadmap.append(entry)

    return roadmap
