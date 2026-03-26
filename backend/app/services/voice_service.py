AGENT_STATE_PROMPTS = [
    "Please share your age.",
    "What is your monthly in-hand income?",
    "What are your monthly expenses?",
    "Do you already invest in SIPs, PF, or stocks?",
    "What is your top financial goal for the next 5 years?",
]


def detect_language(text: str, fallback: str = "en") -> str:
    normalized = text.strip().lower()
    if not normalized:
        return fallback
    # Lightweight heuristic for hackathon prototype to avoid external language deps.
    if any(token in normalized for token in ["namaste", "aap", "paisa", "rupaye"]):
        return "hi"
    if any(token in normalized for token in ["vanakkam", "ungal", "panam"]):
        return "ta"
    if any(token in normalized for token in ["namaskaram", "mee", "dabbu"]):
        return "te"
    if any(token in normalized for token in ["nomoskar", "apnar", "taka"]):
        return "bn"
    return "en"


def respond(mode: str, text: str, turn: int) -> str:
    if mode == "ask":
        return (
            "Quick answer: Based on what you shared, start with emergency fund first, then "
            "invest consistently in a diversified SIP aligned with your risk profile."
        )
    idx = min(turn, len(AGENT_STATE_PROMPTS) - 1)
    return AGENT_STATE_PROMPTS[idx]
