"""Life event financial advisor – bonus, inheritance, marriage, new baby."""

from typing import Any


_EVENT_TEMPLATES: dict[str, dict[str, Any]] = {
    "bonus": {
        "title": "Bonus Windfall Strategy",
        "priority_order": [
            "Clear high-interest debt (credit cards, personal loans)",
            "Top-up emergency fund to 6 months of expenses",
            "Maximize 80C via ELSS/PPF/NPS",
            "Invest remainder in diversified mutual funds",
        ],
    },
    "inheritance": {
        "title": "Inheritance Planning",
        "priority_order": [
            "Park amount in liquid fund while planning",
            "Settle any outstanding debts",
            "Invest for long-term goals (equity + debt mix)",
            "Consider buying adequate term + health insurance",
        ],
    },
    "marriage": {
        "title": "Marriage Financial Prep",
        "priority_order": [
            "Set a realistic wedding budget (max 20-30% of savings)",
            "Open a joint savings account for shared expenses",
            "Review and consolidate insurance policies",
            "Plan combined HRA and tax optimization",
        ],
    },
    "new_baby": {
        "title": "New Baby Financial Checklist",
        "priority_order": [
            "Increase health insurance cover (family floater)",
            "Start a child education SIP (15-18 year horizon)",
            "Increase term life cover by 10-15x annual income",
            "Build a ₹1-2 lakh delivery + first year corpus",
        ],
    },
}


def advise_life_event(
    event_type: str,
    amount: float,
    profile: dict[str, Any],
) -> dict[str, Any]:
    template = _EVENT_TEMPLATES.get(event_type, _EVENT_TEMPLATES["bonus"])

    income = profile.get("income", 0)
    expenses = profile.get("expenses", 0)
    monthly_surplus = max(income / 12 - expenses, 0)

    # Build specific allocation
    allocations: list[dict[str, Any]] = []
    remaining = amount

    if event_type in ("bonus", "inheritance"):
        # 30% debt clear, 20% emergency, 20% 80C, 30% invest
        splits = [
            ("Debt Clearance", 0.30),
            ("Emergency Fund", 0.20),
            ("Tax-Saving (80C)", 0.20),
            ("Long-Term Investment", 0.30),
        ]
        for label, pct in splits:
            alloc_amt = round(remaining * pct)
            allocations.append({"category": label, "amount": alloc_amt, "percentage": int(pct * 100)})
    elif event_type == "marriage":
        splits = [
            ("Wedding Budget", 0.40),
            ("Joint Emergency Fund", 0.20),
            ("Insurance Upgrade", 0.15),
            ("Joint Investments", 0.25),
        ]
        for label, pct in splits:
            allocations.append({"category": label, "amount": round(amount * pct), "percentage": int(pct * 100)})
    else:  # new_baby
        splits = [
            ("Health Insurance Upgrade", 0.15),
            ("Child Education SIP", 0.35),
            ("Term Life Top-up", 0.15),
            ("Delivery + First Year", 0.20),
            ("Emergency Buffer", 0.15),
        ]
        for label, pct in splits:
            allocations.append({"category": label, "amount": round(amount * pct), "percentage": int(pct * 100)})

    # Goal impact
    goal_impact = []
    if monthly_surplus > 0:
        extra_monthly = amount / 12
        goal_impact.append(
            f"This additional ₹{int(extra_monthly):,}/month could accelerate your goals by ~{max(int(extra_monthly / monthly_surplus * 100), 1)}%."
        )

    # Tax impact
    tax_note = ""
    if event_type == "bonus":
        slab_rate = 0.30 if income > 1000000 else (0.20 if income > 500000 else 0.05)
        tax_on_bonus = amount * slab_rate
        tax_note = f"Estimated tax on bonus: ₹{int(tax_on_bonus):,}. Consider investing up to ₹1,50,000 in 80C to reduce liability."
    elif event_type == "inheritance":
        tax_note = "Inheritance is tax-free in India, but income earned on it (interest, dividends) is taxable."

    return {
        "event_type": event_type,
        "title": template["title"],
        "amount": amount,
        "priority_steps": template["priority_order"],
        "allocations": allocations,
        "goal_impact": goal_impact,
        "tax_note": tax_note,
        "monthly_surplus_change": int(amount / 12),
        "explanation": (
            "This is a simplified advisory for educational purposes. "
            "Consult a SEBI-registered advisor for personalized advice."
        ),
    }
