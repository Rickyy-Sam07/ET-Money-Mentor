"""Recommendations engine – personalised advice based on user segmentation."""

from typing import Any


def _segment_user(profile: dict[str, Any]) -> str:
    income = profile.get("income", 0)
    savings_rate = 0
    if income > 0:
        expenses = profile.get("expenses", 0)
        savings_rate = (income / 12 - expenses) / (income / 12) if income > 0 else 0

    if income > 2000000 and savings_rate > 0.3:
        return "high_income_high_saver"
    if income > 2000000:
        return "high_income_low_saver"
    if income > 800000 and savings_rate > 0.3:
        return "mid_income_high_saver"
    if income > 800000:
        return "mid_income_moderate"
    return "early_career"


_FUND_DB: list[dict[str, Any]] = [
    {"name": "Parag Parikh Flexicap Fund", "category": "Flexicap", "risk": "moderate", "return_3y": 18.5, "expense": 0.63},
    {"name": "Mirae Asset Large Cap Fund", "category": "Large Cap", "risk": "moderate", "return_3y": 15.2, "expense": 0.53},
    {"name": "Axis Small Cap Fund", "category": "Small Cap", "risk": "high", "return_3y": 22.1, "expense": 0.56},
    {"name": "HDFC Balanced Advantage Fund", "category": "Balanced", "risk": "low", "return_3y": 14.8, "expense": 0.72},
    {"name": "SBI Magnum Gilt Fund", "category": "Gilt", "risk": "low", "return_3y": 8.2, "expense": 0.46},
    {"name": "Kotak Equity Arbitrage Fund", "category": "Arbitrage", "risk": "very_low", "return_3y": 6.5, "expense": 0.43},
    {"name": "ICICI Pru Nifty Next 50 Index", "category": "Index", "risk": "moderate", "return_3y": 16.8, "expense": 0.30},
    {"name": "Nippon India Liquid Fund", "category": "Liquid", "risk": "very_low", "return_3y": 6.1, "expense": 0.20},
]


def get_recommendations(profile: dict[str, Any]) -> dict[str, Any]:
    segment = _segment_user(profile)
    risk = profile.get("risk_profile", "moderate")

    # Filter funds by risk appetite
    risk_map = {
        "conservative": {"very_low", "low"},
        "moderate": {"very_low", "low", "moderate"},
        "aggressive": {"very_low", "low", "moderate", "high"},
    }
    allowed = risk_map.get(risk, risk_map["moderate"])
    suitable_funds = [f for f in _FUND_DB if f["risk"] in allowed]

    # Sort by 3-year returns
    suitable_funds.sort(key=lambda x: x["return_3y"], reverse=True)
    top_funds = suitable_funds[:5]

    # Asset allocation recommendation
    alloc_map = {
        "early_career": {"equity": 70, "debt": 15, "gold": 10, "liquid": 5},
        "mid_income_moderate": {"equity": 60, "debt": 25, "gold": 10, "liquid": 5},
        "mid_income_high_saver": {"equity": 65, "debt": 20, "gold": 10, "liquid": 5},
        "high_income_low_saver": {"equity": 50, "debt": 30, "gold": 10, "liquid": 10},
        "high_income_high_saver": {"equity": 55, "debt": 25, "gold": 10, "liquid": 10},
    }
    allocation = alloc_map.get(segment, alloc_map["mid_income_moderate"])

    # Insurance recommendations
    income = profile.get("income", 0)
    insurance_recs = []
    insurance_recs.append({
        "type": "Term Life",
        "recommendation": f"Cover of ₹{int(income * 10):,} (10x annual income)",
        "estimated_premium": f"₹{int(income * 0.003):,}/year",
    })
    insurance_recs.append({
        "type": "Health Insurance",
        "recommendation": "Family floater of ₹10,00,000 minimum",
        "estimated_premium": "₹15,000-25,000/year",
    })

    # Tax-saving recommendations
    tax_recs = []
    investments = profile.get("investments", [])
    used_80c = sum(
        inv.get("amount", 0) for inv in investments
        if inv.get("type") in ("ELSS", "PPF", "NPS", "EPF", "LIC")
    )
    gap_80c = max(150000 - used_80c, 0)
    if gap_80c > 0:
        tax_recs.append({
            "section": "80C",
            "gap": int(gap_80c),
            "suggestion": f"Invest ₹{int(gap_80c):,} more in ELSS/PPF/NPS to save up to ₹{int(gap_80c * 0.3):,} in tax.",
        })
    tax_recs.append({
        "section": "80CCD(1B)",
        "gap": 50000,
        "suggestion": "Additional ₹50,000 in NPS gives extra deduction beyond 80C limit.",
    })

    return {
        "segment": segment,
        "risk_profile": risk,
        "recommended_funds": top_funds,
        "asset_allocation": allocation,
        "insurance": insurance_recs,
        "tax_saving": tax_recs,
        "explanation": (
            f"Based on your profile segment ({segment.replace('_', ' ')}), "
            "these recommendations balance growth and safety. "
            "Consult a SEBI-registered advisor before investing."
        ),
    }
