"""Couple's Money Planner – joint optimization of HRA, NPS, SIP, insurance, net worth."""

from typing import Any


def _optimal_hra(p1: dict[str, Any], p2: dict[str, Any]) -> dict[str, Any]:
    """Higher income partner should claim HRA for maximum benefit."""
    p1_income = p1.get("income", 0)
    p2_income = p2.get("income", 0)
    rent = max(p1.get("rent", 0), p2.get("rent", 0))

    if rent <= 0:
        return {"suggestion": "Neither partner pays rent; HRA not applicable.", "tax_saved": 0}

    if p1_income >= p2_income:
        claimer = "Partner 1"
        income = p1_income
    else:
        claimer = "Partner 2"
        income = p2_income

    # Simplified HRA exemption: min(actual HRA, 50% of salary, rent - 10% salary)
    basic = income * 0.4  # approximate basic
    hra_received = basic * 0.4
    exemption = min(hra_received, basic * 0.5, max(rent * 12 - basic * 0.1, 0))
    tax_rate = 0.30 if income > 1000000 else 0.20
    saved = int(exemption * tax_rate)

    return {
        "suggestion": f"{claimer} (higher income) should claim HRA. Estimated exemption: ₹{int(exemption):,}.",
        "claimer": claimer,
        "exemption": int(exemption),
        "tax_saved": saved,
    }


def _nps_matching(p1: dict[str, Any], p2: dict[str, Any]) -> dict[str, Any]:
    """Both partners should contribute to NPS for 80CCD(1B) benefit."""
    p1_nps = p1.get("nps_contribution", 0)
    p2_nps = p2.get("nps_contribution", 0)
    max_benefit = 50000

    suggestions = []
    total_additional = 0

    if p1_nps < max_benefit:
        gap = max_benefit - p1_nps
        suggestions.append(f"Partner 1 can contribute ₹{int(gap):,} more to NPS (80CCD(1B)).")
        total_additional += gap
    if p2_nps < max_benefit:
        gap = max_benefit - p2_nps
        suggestions.append(f"Partner 2 can contribute ₹{int(gap):,} more to NPS (80CCD(1B)).")
        total_additional += gap

    tax_saved = int(total_additional * 0.30)

    return {
        "suggestions": suggestions,
        "additional_contribution": int(total_additional),
        "combined_tax_saved": tax_saved,
    }


def _sip_splits(p1: dict[str, Any], p2: dict[str, Any]) -> list[dict[str, Any]]:
    """Split SIPs based on tax brackets."""
    p1_surplus = max(p1.get("income", 0) / 12 - p1.get("expenses", 0), 0)
    p2_surplus = max(p2.get("income", 0) / 12 - p2.get("expenses", 0), 0)
    total = p1_surplus + p2_surplus

    if total <= 0:
        return [{"goal": "General", "partner1_sip": 0, "partner2_sip": 0}]

    p1_ratio = p1_surplus / total if total > 0 else 0.5
    p2_ratio = 1 - p1_ratio

    goals = [
        {"goal": "Retirement", "total_sip": int(total * 0.40)},
        {"goal": "House Down-Payment", "total_sip": int(total * 0.25)},
        {"goal": "Child Education", "total_sip": int(total * 0.20)},
        {"goal": "Emergency Buffer", "total_sip": int(total * 0.15)},
    ]

    return [
        {
            "goal": g["goal"],
            "partner1_sip": int(g["total_sip"] * p1_ratio),
            "partner2_sip": int(g["total_sip"] * p2_ratio),
            "total_sip": g["total_sip"],
        }
        for g in goals
    ]


def _insurance_plan(p1: dict[str, Any], p2: dict[str, Any]) -> dict[str, Any]:
    p1_income = p1.get("income", 0)
    p2_income = p2.get("income", 0)

    recommended_term = int((p1_income + p2_income) * 10)
    recommended_health = 1000000  # ₹10L family floater

    return {
        "term_life_cover": f"₹{recommended_term:,} combined term plan",
        "health_cover": f"₹{recommended_health:,} family floater",
        "suggestion": (
            "Get a joint family floater for health. "
            "For term life, each partner should have individual cover of 10x their income."
        ),
    }


def _net_worth_projection(p1: dict[str, Any], p2: dict[str, Any]) -> list[dict[str, Any]]:
    p1_invested = sum(inv.get("amount", 0) for inv in p1.get("investments", []))
    p2_invested = sum(inv.get("amount", 0) for inv in p2.get("investments", []))
    combined = p1_invested + p2_invested

    monthly_sip = max(p1.get("income", 0) / 12 - p1.get("expenses", 0), 0) + \
                  max(p2.get("income", 0) / 12 - p2.get("expenses", 0), 0)
    annual_sip = monthly_sip * 12

    projections = []
    corpus = combined
    for year in range(1, 11):
        corpus = corpus * 1.12 + annual_sip
        projections.append({"year": year, "net_worth": int(corpus)})

    return projections


def optimize_couple(p1: dict[str, Any], p2: dict[str, Any]) -> dict[str, Any]:
    return {
        "hra_optimization": _optimal_hra(p1, p2),
        "nps_matching": _nps_matching(p1, p2),
        "sip_splits": _sip_splits(p1, p2),
        "insurance": _insurance_plan(p1, p2),
        "net_worth_projection": _net_worth_projection(p1, p2),
        "explanation": (
            "This joint plan optimizes tax benefits and investment allocation for both partners. "
            "Consult a SEBI-registered advisor for personalized advice."
        ),
    }
