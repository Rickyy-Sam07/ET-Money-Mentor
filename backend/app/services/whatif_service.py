"""What-if simulation – scenario analysis for windfalls and changes."""

from typing import Any


def simulate_whatif(
    scenario: str,
    amount: float,
    profile: dict[str, Any],
) -> dict[str, Any]:
    income = profile.get("income", 0)
    expenses = profile.get("expenses", 0)
    monthly_surplus = max(income / 12 - expenses, 0)
    current_investments = sum(inv.get("amount", 0) for inv in profile.get("investments", []))

    scenarios: list[dict[str, Any]] = []

    # Scenario 1: Invest all
    def _project(lump: float, monthly: float, rate: float, years: int) -> int:
        corpus = lump
        for _ in range(years * 12):
            corpus = corpus * (1 + rate / 12) + monthly
        return int(corpus)

    base_5y = _project(current_investments, monthly_surplus, 0.12, 5)
    base_10y = _project(current_investments, monthly_surplus, 0.12, 10)

    # Scenario A: Invest entire amount
    invest_all_5 = _project(current_investments + amount, monthly_surplus, 0.12, 5)
    invest_all_10 = _project(current_investments + amount, monthly_surplus, 0.12, 10)
    scenarios.append({
        "name": "Invest All",
        "description": f"Invest the entire ₹{int(amount):,} in diversified mutual funds.",
        "allocation": {"equity": 60, "debt": 30, "gold": 10},
        "projected_5y": invest_all_5,
        "projected_10y": invest_all_10,
        "gain_over_base_5y": invest_all_5 - base_5y,
        "gain_over_base_10y": invest_all_10 - base_10y,
        "risk": "moderate",
    })

    # Scenario B: 50% invest + 50% spend/enjoy
    half = amount / 2
    split_5 = _project(current_investments + half, monthly_surplus, 0.12, 5)
    split_10 = _project(current_investments + half, monthly_surplus, 0.12, 10)
    scenarios.append({
        "name": "Split 50-50",
        "description": f"Invest ₹{int(half):,} and use ₹{int(half):,} for lifestyle/goals.",
        "allocation": {"invest": 50, "spend": 50},
        "projected_5y": split_5,
        "projected_10y": split_10,
        "gain_over_base_5y": split_5 - base_5y,
        "gain_over_base_10y": split_10 - base_10y,
        "risk": "low",
    })

    # Scenario C: Repay debt + invest remainder
    debt_emi = profile.get("debt_emi", 0) * 12
    debt_payoff = min(amount * 0.6, debt_emi * 2) if debt_emi > 0 else 0
    invest_remainder = amount - debt_payoff
    debt_5 = _project(current_investments + invest_remainder, monthly_surplus + debt_payoff / 60, 0.12, 5)
    debt_10 = _project(current_investments + invest_remainder, monthly_surplus + debt_payoff / 120, 0.12, 10)
    scenarios.append({
        "name": "Repay Debt First",
        "description": (
            f"Use ₹{int(debt_payoff):,} to clear/reduce debt, invest ₹{int(invest_remainder):,}."
            if debt_payoff > 0 else
            f"No significant debt. Invest the full ₹{int(amount):,} instead."
        ),
        "allocation": {"debt_repayment": int(debt_payoff), "investment": int(invest_remainder)},
        "projected_5y": debt_5,
        "projected_10y": debt_10,
        "gain_over_base_5y": debt_5 - base_5y,
        "gain_over_base_10y": debt_10 - base_10y,
        "risk": "conservative",
    })

    return {
        "scenario_description": scenario,
        "amount": amount,
        "base_projection": {"year_5": base_5y, "year_10": base_10y},
        "scenarios": scenarios,
        "recommendation": (
            "For most people, a balanced approach (Scenario B) works best. "
            "If you have high-cost debt, prioritize repayment (Scenario C)."
        ),
        "explanation": (
            "Projections assume 12% annual return for equity-heavy portfolios. "
            "Actual returns may vary. This is for educational purposes only."
        ),
    }
