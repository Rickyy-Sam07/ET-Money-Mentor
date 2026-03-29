"""Emergency chatbot – empathetic, actionable crisis responses."""

from typing import Any


_CRISIS_PLAYBOOKS: dict[str, dict[str, Any]] = {
    "job_loss": {
        "title": "Job Loss Recovery Plan",
        "empathy": "Losing a job is stressful, but you have options. Let's build a plan together.",
        "steps": [
            {
                "action": "Assess your emergency fund",
                "detail": "Check how many months of expenses your emergency fund covers. Target: 6 months.",
                "priority": "immediate",
            },
            {
                "action": "Apply for EPF advance",
                "detail": "You can withdraw up to 75% of your EPF balance after 1 month of unemployment. Apply via the EPFO portal.",
                "priority": "within_1_week",
                "link": "https://www.epfindia.gov.in",
            },
            {
                "action": "Reduce discretionary spending",
                "detail": "Cut non-essential expenses by 30-50% immediately.",
                "priority": "immediate",
            },
            {
                "action": "Do NOT break long-term investments",
                "detail": "Avoid redeeming ELSS, PPF, or equity MFs unless absolutely necessary.",
                "priority": "important",
            },
            {
                "action": "Explore health insurance",
                "detail": "If employer coverage ends, get an individual health policy immediately (before any waiting period).",
                "priority": "within_1_week",
            },
            {
                "action": "Upskill and network",
                "detail": "Use free resources (Coursera, LinkedIn Learning) and update your resume.",
                "priority": "ongoing",
            },
        ],
    },
    "medical": {
        "title": "Medical Emergency Response",
        "empathy": "Health comes first. Let's ensure you're financially covered during this time.",
        "steps": [
            {
                "action": "File insurance claim immediately",
                "detail": "Contact your insurer's TPA for cashless hospitalisation or reimbursement. Keep all bills.",
                "priority": "immediate",
            },
            {
                "action": "Use emergency fund",
                "detail": "Use your emergency fund for out-of-pocket expenses while claim is processed.",
                "priority": "immediate",
            },
            {
                "action": "Check employer benefits",
                "detail": "Many employers offer advance salary or medical loans at 0% interest.",
                "priority": "within_1_week",
            },
            {
                "action": "Avoid high-interest borrowing",
                "detail": "Do NOT use credit card EMI or personal loans if avoidable.",
                "priority": "important",
            },
            {
                "action": "Government schemes",
                "detail": "Check eligibility for Ayushman Bharat (₹5L cover) or state health schemes.",
                "priority": "within_1_week",
                "link": "https://pmjay.gov.in",
            },
        ],
    },
    "debt_crisis": {
        "title": "Debt Crisis Management",
        "empathy": "Debt can feel overwhelming, but structured repayment can get you out. Let's plan.",
        "steps": [
            {
                "action": "List all debts with interest rates",
                "detail": "Rank from highest interest rate to lowest (avalanche method).",
                "priority": "immediate",
            },
            {
                "action": "Negotiate with lenders",
                "detail": "Call your bank and ask for restructuring, moratorium, or lower rates.",
                "priority": "within_1_week",
            },
            {
                "action": "Consolidate if possible",
                "detail": "Transfer high-rate credit card debt to a lower-rate personal loan.",
                "priority": "within_1_week",
            },
            {
                "action": "Cut expenses to bare minimum",
                "detail": "Follow the 50/30/20 rule, but shift to 50/10/40 (40% to debt).",
                "priority": "immediate",
            },
            {
                "action": "Avoid new debt",
                "detail": "Freeze credit cards. Use only debit card or cash.",
                "priority": "ongoing",
            },
        ],
    },
    "market_crash": {
        "title": "Market Crash Response",
        "empathy": "Market corrections are scary but normal. Let's protect your wealth rationally.",
        "steps": [
            {
                "action": "Do NOT panic sell",
                "detail": "Historically, markets recover. Selling locks in losses.",
                "priority": "immediate",
            },
            {
                "action": "Continue SIPs",
                "detail": "Market dips mean you buy more units at lower NAVs. This is rupee-cost averaging.",
                "priority": "ongoing",
            },
            {
                "action": "Review asset allocation",
                "detail": "If equities dropped below your target allocation, this is a rebalancing opportunity.",
                "priority": "within_1_week",
            },
            {
                "action": "Avoid leveraged positions",
                "detail": "Do not use margin trading or borrow to invest during volatile markets.",
                "priority": "important",
            },
            {
                "action": "Consider increasing SIP",
                "detail": "If you have surplus cash, consider topping up SIPs during corrections.",
                "priority": "optional",
            },
        ],
    },
}


def respond_emergency(
    crisis_type: str,
    details: str,
    profile: dict[str, Any],
) -> dict[str, Any]:
    playbook = _CRISIS_PLAYBOOKS.get(crisis_type, _CRISIS_PLAYBOOKS["job_loss"])

    emergency_fund = profile.get("emergency_fund", 0)
    expenses = profile.get("expenses", 0)
    months_covered = round(emergency_fund / expenses, 1) if expenses > 0 else 0

    personalised_note = ""
    if months_covered >= 6:
        personalised_note = f"Good news: your emergency fund covers ~{months_covered} months. You have time to plan carefully."
    elif months_covered >= 3:
        personalised_note = f"Your emergency fund covers ~{months_covered} months. Be careful with spending while you recover."
    else:
        personalised_note = f"Your emergency fund covers only ~{months_covered} months. Prioritise essential expenses immediately."

    return {
        "crisis_type": crisis_type,
        "title": playbook["title"],
        "empathy_message": playbook["empathy"],
        "personalised_note": personalised_note,
        "action_steps": playbook["steps"],
        "emergency_fund_months": months_covered,
        "explanation": (
            "This is a crisis-response guide for educational purposes. "
            "For legal or medical advice, please consult relevant professionals."
        ),
    }
