from typing import Any


def _calculate_old_regime_tax(taxable_income: float) -> float:
    # Simplified slab model for prototype purposes.
    if taxable_income <= 250000:
        return 0.0
    if taxable_income <= 500000:
        return (taxable_income - 250000) * 0.05
    if taxable_income <= 1000000:
        return 12500 + (taxable_income - 500000) * 0.2
    return 112500 + (taxable_income - 1000000) * 0.3


def _calculate_new_regime_tax(taxable_income: float) -> float:
    # Simplified slab model for prototype purposes.
    if taxable_income <= 300000:
        return 0.0
    if taxable_income <= 700000:
        return (taxable_income - 300000) * 0.05
    if taxable_income <= 1000000:
        return 20000 + (taxable_income - 700000) * 0.1
    if taxable_income <= 1200000:
        return 50000 + (taxable_income - 1000000) * 0.15
    if taxable_income <= 1500000:
        return 80000 + (taxable_income - 1200000) * 0.2
    return 140000 + (taxable_income - 1500000) * 0.3


def analyze_tax(form16_data: dict[str, Any], regime_preference: str) -> dict[str, Any]:
    salary = float(form16_data.get("gross_salary", 0))
    used_80c = float(form16_data.get("deductions_80c", 0))
    used_80d = float(form16_data.get("deductions_80d", 0))

    max_80c = 150000
    max_80d = 25000

    missed_80c = max(max_80c - used_80c, 0)
    missed_80d = max(max_80d - used_80d, 0)

    deductions_total = used_80c + used_80d
    taxable_old = max(salary - deductions_total, 0)
    taxable_new = salary

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

    return {
        "salary": salary,
        "deductions": {
            "used_80c": used_80c,
            "used_80d": used_80d,
            "missed_80c": missed_80c,
            "missed_80d": missed_80d,
        },
        "regime_comparison": {
            "old": old_tax,
            "new": new_tax,
            "selected": preferred,
            "recommended": suggested,
        },
        "suggestions": investments,
        "explanation": (
            "This estimate is educational. It compares simplified old vs new regime calculations "
            "using your provided salary and declared deductions."
        ),
    }
