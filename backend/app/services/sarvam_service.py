# [DEV1] sarvam_service.py — Sarvam AI STT + TTS. Dev2: do not modify.
import base64
import json
import os
import tempfile
import time
from pathlib import Path

import requests


def _retry_call(fn, *, max_attempts_env: str = "SARVAM_MAX_RETRIES", default_attempts: str = "3"):
    max_attempts = int(os.getenv(max_attempts_env, default_attempts))
    backoff = 1.0
    last_error: Exception | None = None

    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as exc:
            last_error = exc
            if attempt < max_attempts - 1:
                time.sleep(backoff)
                backoff *= 2
                continue

    raise RuntimeError(f"Sarvam call failed after retries: {last_error}")


def _download_audio_with_retry(url: str) -> bytes:
    timeout_sec = int(os.getenv("SARVAM_AUDIO_FETCH_TIMEOUT_SEC", "30"))

    def _fetch() -> bytes:
        data = requests.get(url, timeout=timeout_sec)
        if data.status_code in {429, 500, 502, 503, 504}:
            data.raise_for_status()
        data.raise_for_status()
        return data.content

    return _retry_call(_fetch)


def _get_sarvam_key() -> str:
    key = os.getenv("SARVAM_API_SUBSCRIPTION_KEY") or os.getenv("SARVAM_API_KEY")
    if not key:
        raise ValueError("Missing SARVAM_API_SUBSCRIPTION_KEY or SARVAM_API_KEY environment variable.")
    return key


def _extract_transcript_from_outputs(output_dir: str) -> str:
    base = Path(output_dir)

    for path in base.rglob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
            if isinstance(data, dict):
                for key in ("transcript", "text", "normalized_text"):
                    if data.get(key):
                        return str(data[key]).strip()
        except Exception:
            continue

    for path in base.rglob("*.txt"):
        text = path.read_text(encoding="utf-8", errors="ignore").strip()
        if text:
            return text

    return ""


def transcribe_audio_file(file_path: str) -> str:
    from sarvamai import SarvamAI
    client = SarvamAI(api_subscription_key=_get_sarvam_key())
    job = _retry_call(
        lambda: client.speech_to_text_job.create_job(
            model="saaras:v3",
            mode="transcribe",
            language_code="unknown",
            with_diarization=True,
            num_speakers=2,
        )
    )

    _retry_call(lambda: job.upload_files(file_paths=[file_path]))
    _retry_call(job.start)
    _retry_call(job.wait_until_complete)

    transcript = ""
    file_results = job.get_file_results()
    for row in file_results.get("successful", []):
        for key in ("transcript", "text", "normalized_text"):
            if row.get(key):
                transcript = str(row[key]).strip()
                break
        if transcript:
            break

    if not transcript:
        with tempfile.TemporaryDirectory(prefix="sarvam_output_") as output_dir:
            job.download_outputs(output_dir=output_dir)
            transcript = _extract_transcript_from_outputs(output_dir)

    if not transcript:
        raise RuntimeError("Unable to extract transcript from Sarvam STT job output.")

    return transcript


def _map_language_code(code: str | None) -> str:
    mapping = {
        "hi": "hi-IN",
        "en": "en-IN",
        "ta": "en-IN",
        "te": "en-IN",
        "bn": "bn-IN",
    }
    return mapping.get((code or "en").lower(), "en-IN")


def _map_speaker(lang_code: str) -> str:
    # Use shubh for English, Hindi, and Bengali voice output.
    mapping = {
        "en-IN": "shubh",
        "hi-IN": "shubh",
        "bn-IN": "shubh",
    }
    return mapping.get(lang_code, "shubh")


def synthesize_text(text: str, detected_language: str | None = None) -> tuple[str, str]:
    from sarvamai import SarvamAI

    key = _get_sarvam_key()
    target_lang = _map_language_code(detected_language)
    speaker = _map_speaker(target_lang)

    client = SarvamAI(api_subscription_key=key)

    def _call() -> str:
        response = client.text_to_speech.convert(
            text=text,
            target_language_code=target_lang,
            speaker=speaker,
            model="bulbul:v3",
            pace=1.1,
            speech_sample_rate=22050,
            output_audio_codec="wav",
            enable_preprocessing=True,
        )
        audios = list(getattr(response, "audios", []) or [])
        if not audios:
            raise RuntimeError("Sarvam TTS returned no audio payload.")
        return str(audios[0]).strip()

    audio_base64 = _retry_call(_call)
    if not audio_base64:
        raise RuntimeError("Sarvam TTS returned an empty audio payload.")
    return audio_base64, "audio/wav"
