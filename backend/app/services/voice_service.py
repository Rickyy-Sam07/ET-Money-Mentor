# [DEV1] voice_service.py — language detection + agent state prompts. Dev2: do not modify.
from app.services.groq_service import detect_language_llm

AGENT_STATE_PROMPTS = [
    "Please share your age.",
    "What is your monthly in-hand income?",
    "What are your monthly expenses?",
    "Do you already invest in SIPs, PF, or stocks?",
    "What is your top financial goal for the next 5 years?",
]


def detect_language(text: str, fallback: str = "en") -> str:
    return detect_language_llm(text, fallback=fallback)


def respond(mode: str, text: str, turn: int) -> str:
    if mode == "ask":
        return (
            "Quick answer: Based on what you shared, start with emergency fund first, then "
            "invest consistently in a diversified SIP aligned with your risk profile."
        )
    idx = min(turn, len(AGENT_STATE_PROMPTS) - 1)
    return AGENT_STATE_PROMPTS[idx]
