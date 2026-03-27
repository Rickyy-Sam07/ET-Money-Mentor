import os
import time
import json
from typing import Any

import requests

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def _post_with_retry(headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    timeout_sec = int(os.getenv("GROQ_TIMEOUT_SEC", "20"))
    max_attempts = int(os.getenv("GROQ_MAX_RETRIES", "3"))
    backoff = 1.0

    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            response = requests.post(GROQ_URL, headers=headers, json=payload, timeout=timeout_sec)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < max_attempts - 1:
                time.sleep(backoff)
                backoff *= 2
                continue
            response.raise_for_status()
            return response.json()
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts - 1:
                time.sleep(backoff)
                backoff *= 2
                continue

    raise RuntimeError(f"Groq request failed after retries: {last_error}")


def _fallback_response(mode: str, turn: int) -> str:
    prompts = [
        "Please share your age.",
        "What is your monthly in-hand income?",
        "What are your monthly expenses?",
        "Do you already invest in SIPs, PF, or stocks?",
        "What is your top financial goal for the next 5 years?",
    ]
    if mode == "ask":
        return "Start by building a 6-month emergency fund, then automate SIPs aligned with your risk profile."
    return prompts[min(turn, len(prompts) - 1)]


def generate_mentor_response(
    mode: str,
    user_text: str,
    detected_language: str,
    turn: int,
    market_signal: dict[str, Any] | None = None,
) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _fallback_response(mode, turn)

    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    market_note = market_signal or {"label": "neutral", "reason": "No market signal supplied."}

    system_prompt = (
        "You are ET Money Mentor. Give concise, practical, India-focused personal finance guidance. "
        "Never promise guaranteed returns. Mention risk where relevant. "
        f"Current market signal: {market_note.get('label')} ({market_note.get('reason')})."
    )

    user_prompt = (
        f"Mode: {mode}\n"
        f"Detected language: {detected_language}\n"
        f"Conversation turn: {turn}\n"
        f"User said: {user_text}\n"
        "Return exactly one short sentence (max 14 words). Be direct and practical."
    )

    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        data = _post_with_retry(headers=headers, payload=payload)
        message = data["choices"][0]["message"]["content"].strip()
        return message or _fallback_response(mode, turn)
    except Exception:
        return _fallback_response(mode, turn)


def _fallback_command_intent(transcript: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
    t = transcript.lower()
    known_ids = {str(row.get("id", "")).strip() for row in commands}

    def exists(command_id: str) -> bool:
        return command_id in known_ids

    if any(token in t for token in ["help", "madad", "commands"]):
        return {"command_id": "help", "confidence": 0.45, "reason": "fallback keyword match"}

    if any(token in t for token in ["upload", "file", "document"]) and exists("navigate_upload"):
        return {"command_id": "navigate_upload", "confidence": 0.55, "reason": "fallback keyword match"}
    if any(token in t for token in ["tax", "80c", "80d", "salary"]) and exists("run_tax"):
        return {"command_id": "run_tax", "confidence": 0.55, "reason": "fallback keyword match"}
    if "portfolio" in t and exists("run_portfolio"):
        return {"command_id": "run_portfolio", "confidence": 0.55, "reason": "fallback keyword match"}
    if any(token in t for token in ["news", "market", "khabar"]) and exists("run_news"):
        return {"command_id": "run_news", "confidence": 0.55, "reason": "fallback keyword match"}
    if "report" in t and exists("generate_report"):
        return {"command_id": "generate_report", "confidence": 0.55, "reason": "fallback keyword match"}

    return {"command_id": "unknown", "confidence": 0.0, "reason": "no fallback keyword match"}


def _extract_json_block(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            parsed = json.loads(text[start : end + 1])
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return None
    return None


def resolve_voice_command_intent(transcript: str, commands: list[dict[str, Any]]) -> dict[str, Any]:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return _fallback_command_intent(transcript, commands)

    command_lines = []
    for item in commands:
        command_lines.append(
            {
                "id": item.get("id"),
                "description": item.get("description"),
                "examples": item.get("examples", []),
            }
        )

    system_prompt = (
        "You are an intent classifier for a voice-command UI. "
        "Given a transcript and allowed commands, return ONLY strict JSON with keys: "
        "command_id (string), confidence (0..1 number), reason (string). "
        "Pick only one id from provided commands, else return command_id as 'unknown'."
    )
    user_prompt = (
        f"Transcript: {transcript}\n"
        f"Allowed commands: {json.dumps(command_lines, ensure_ascii=True)}\n"
        "Output JSON only."
    )

    payload = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "temperature": 0,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    try:
        data = _post_with_retry(headers=headers, payload=payload)
        content = str(data["choices"][0]["message"]["content"])
        parsed = _extract_json_block(content)
        if not parsed:
            return _fallback_command_intent(transcript, commands)

        allowed_ids = {str(row.get("id", "")).strip() for row in commands}
        command_id = str(parsed.get("command_id", "unknown")).strip() or "unknown"
        if command_id not in allowed_ids and command_id != "unknown":
            command_id = "unknown"

        confidence = parsed.get("confidence", 0)
        try:
            confidence = float(confidence)
        except Exception:
            confidence = 0.0
        confidence = max(0.0, min(confidence, 1.0))

        reason = str(parsed.get("reason", "llm classification")).strip()
        return {"command_id": command_id, "confidence": confidence, "reason": reason}
    except Exception:
        return _fallback_command_intent(transcript, commands)
