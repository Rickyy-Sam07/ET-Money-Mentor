"""Groq LLM client – generates plain-English financial explanations."""

import os
from typing import Any

from dotenv import load_dotenv

load_dotenv()

_GROQ_KEY = os.getenv("GROQ_API_KEY", "")
_client = None


def _get_client():
    global _client
    if _client is None and _GROQ_KEY:
        from groq import Groq
        _client = Groq(api_key=_GROQ_KEY)
    return _client


SYSTEM_PROMPT = (
    "You are an expert Indian financial advisor AI for the ET Money Mentor app. "
    "You give clear, actionable, personalised advice in simple English. "
    "Always mention amounts in ₹ (INR). "
    "Keep responses concise (3-5 sentences max). "
    "Never say 'guaranteed returns'. "
    "Always add a disclaimer that this is educational and users should consult a SEBI-registered advisor."
)


def generate_explanation(context: str, fallback: str = "") -> str:
    """Call Groq LLM to generate a plain-English explanation.
    
    Falls back gracefully to `fallback` text if Groq is unavailable.
    """
    client = _get_client()
    if not client:
        return fallback or "AI explanation unavailable. Please check your Groq API key."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.6,
            max_tokens=300,
        )
        return response.choices[0].message.content or fallback
    except Exception as e:
        return fallback or f"AI explanation temporarily unavailable: {str(e)}"


def generate_emergency_response(crisis_type: str, details: str, profile_summary: str, fallback: str = "") -> str:
    """Generate an empathetic emergency response."""
    client = _get_client()
    if not client:
        return fallback

    emergency_prompt = (
        "You are a compassionate financial crisis counselor. "
        "Be empathetic, calm, and reassuring. "
        "Give 3-5 specific, actionable steps personalised to the user's situation. "
        "Mention government schemes (EPF, Ayushman Bharat, PM Kisan) where applicable. "
        "Never say 'guaranteed returns'. "
        "Add a disclaimer about consulting professionals."
    )

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": emergency_prompt},
                {"role": "user", "content": (
                    f"Crisis type: {crisis_type}\n"
                    f"User details: {details}\n"
                    f"Financial profile: {profile_summary}\n\n"
                    "Give an empathetic, actionable response."
                )},
            ],
            temperature=0.7,
            max_tokens=400,
        )
        return response.choices[0].message.content or fallback
    except Exception:
        return fallback
