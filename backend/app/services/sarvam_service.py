import base64
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any

import requests
from sarvamai import SarvamAI


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


def _get_sarvam_client() -> SarvamAI:
    key = os.getenv("SARVAM_API_SUBSCRIPTION_KEY") or os.getenv("SARVAM_API_KEY")
    if not key:
        raise ValueError("Missing SARVAM_API_SUBSCRIPTION_KEY or SARVAM_API_KEY environment variable.")
    return SarvamAI(api_subscription_key=key)


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
    client = _get_sarvam_client()
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


def _extract_audio_bytes(response: Any) -> bytes:
    if isinstance(response, (bytes, bytearray)):
        return bytes(response)

    if isinstance(response, dict):
        if isinstance(response.get("audios"), list) and response["audios"]:
            first_audio = response["audios"][0]
            if isinstance(first_audio, str) and first_audio.strip():
                return base64.b64decode(first_audio)
        for key in ("audio", "audio_bytes"):
            if isinstance(response.get(key), (bytes, bytearray)):
                return bytes(response[key])
        for key in ("audio_base64", "base64_audio"):
            if isinstance(response.get(key), str) and response[key].strip():
                return base64.b64decode(response[key])
        if isinstance(response.get("audio_url"), str) and response["audio_url"].strip():
            return _download_audio_with_retry(response["audio_url"])

    if hasattr(response, "audio") and isinstance(response.audio, (bytes, bytearray)):
        return bytes(response.audio)
    if hasattr(response, "audios") and isinstance(response.audios, list) and response.audios:
        first_audio = response.audios[0]
        if isinstance(first_audio, str) and first_audio.strip():
            return base64.b64decode(first_audio)
    if hasattr(response, "audio_base64") and isinstance(response.audio_base64, str):
        return base64.b64decode(response.audio_base64)
    if hasattr(response, "audio_url") and isinstance(response.audio_url, str):
        return _download_audio_with_retry(response.audio_url)

    raise RuntimeError("Unable to extract audio bytes from Sarvam TTS response.")


def _map_language_code(code: str | None) -> str:
    mapping = {
        "hi": "hi-IN",
        "en": "en-IN",
        "ta": "ta-IN",
        "te": "te-IN",
        "bn": "bn-IN",
    }
    return mapping.get((code or "hi").lower(), "hi-IN")


def synthesize_text(text: str, detected_language: str | None = None) -> tuple[str, str]:
    client = _get_sarvam_client()
    response = _retry_call(
        lambda: client.text_to_speech.convert(
            text=text,
            target_language_code=_map_language_code(detected_language),
            speaker="sunny",
            pace=1.1,
            speech_sample_rate=22050,
            enable_preprocessing=True,
            model="bulbul:v3",
        )
    )

    audio_bytes = _extract_audio_bytes(response)
    return base64.b64encode(audio_bytes).decode("utf-8"), "audio/wav"
