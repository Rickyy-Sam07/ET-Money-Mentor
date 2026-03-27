from typing import Any


def _with_cess(tax: float) -> float:
    return tax * 1.04


def _calculate_old_regime_tax(taxable_income: float) -> float:
    # FY-like slab approximation including 4% cess and rebate up to 5L taxable.
    tax = 0.0
    if taxable_income > 250000:
        tax += min(taxable_income, 500000) - 250000
        tax *= 0.05
    if taxable_income > 500000:
        tax += (min(taxable_income, 1000000) - 500000) * 0.2
    if taxable_income > 1000000:
        tax += (taxable_income - 1000000) * 0.3

    if taxable_income <= 500000:
        tax = 0.0

    return _with_cess(max(tax, 0.0))


def _calculate_new_regime_tax(taxable_income: float) -> float:
    # FY-like slab approximation including cess and rebate up to 7L taxable.
    slabs = [
        (0, 300000, 0.00),
        (300000, 700000, 0.05),
        (700000, 1000000, 0.10),
        (1000000, 1200000, 0.15),
        (1200000, 1500000, 0.20),
        (1500000, float("inf"), 0.30),
    ]

    tax = 0.0
    for low, high, rate in slabs:
        if taxable_income > low:
            tax += (min(taxable_income, high) - low) * rate

    if taxable_income <= 700000:
        tax = 0.0

    return _with_cess(max(tax, 0.0))


def analyze_tax(form16_data: dict[str, Any], regime_preference: str, market_signal: dict[str, Any] | None = None) -> dict[str, Any]:
    salary = float(form16_data.get("gross_salary", 0))
    used_80c = float(form16_data.get("deductions_80c", 0))
    used_80d = float(form16_data.get("deductions_80d", 0))
    hra_exemption = float(form16_data.get("hra_exemption", 0))
    standard_deduction_old = 50000
    standard_deduction_new = 50000

    max_80c = 150000
    max_80d = 25000

    missed_80c = max(max_80c - used_80c, 0)
    missed_80d = max(max_80d - used_80d, 0)

    deductions_total = used_80c + used_80d
    taxable_old = max(salary - deductions_total - standard_deduction_old - hra_exemption, 0)
    taxable_new = max(salary - standard_deduction_new, 0)

    old_tax = _calculate_old_regime_tax(taxable_old)
    new_tax = _calculate_new_regime_tax(taxable_new)

    preferred = regime_preference if regime_preference in {"old", "new"} else "new"
    suggested = "old" if old_tax < new_tax else "new"

    investments = [
        {
            "instrument": "ELSS",
            "risk": "moderate",
            "liquidity": "3-year lock-in",
            "estimated_tax_saving": min(missed_80c * 0.3, 45000),
        },
        {
            "instrument": "PPF",
            "risk": "low",
            "liquidity": "15-year tenure",
            "estimated_tax_saving": min(missed_80c * 0.2, 30000),
        },
        {
            "instrument": "NPS",
            "risk": "moderate",
            "liquidity": "retirement-linked",
            "estimated_tax_saving": min(50000 * 0.3, 15000),
        },
    ]

    signal = (market_signal or {}).get("label", "neutral")
    if signal == "negative":
        investments.sort(key=lambda row: 0 if row["risk"] == "low" else 1)
    elif signal == "positive":
        investments.sort(key=lambda row: row["estimated_tax_saving"], reverse=True)

    return {
        "salary": salary,
        "deductions": {
            "used_80c": used_80c,
            "used_80d": used_80d,
            "missed_80c": missed_80c,
            "missed_80d": missed_80d,
        },
        "regime_comparison": {
            "old": round(old_tax, 2),
            "new": round(new_tax, 2),
            "selected": preferred,
            "recommended": suggested,
        },
        "suggestions": investments,
        "market_signal": market_signal
        or {"label": "neutral", "score": 0, "reason": "No live news-based market signal available."},
        "explanation": (
            "This estimate is educational. It applies slab, rebate and cess approximations for old/new regimes "
            "using your supplied salary and deduction inputs."
        ),
    }
