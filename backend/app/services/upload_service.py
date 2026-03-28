# [DEV1] upload_service.py — OCR + LLM structured parsing. Dev2: do not modify.
import importlib
import tempfile
from pathlib import Path
from typing import Any

from app.services.groq_service import parse_ocr_to_structured_json

ocr_engine: Any = None


def _get_ocr_engine() -> Any:
    global ocr_engine
    if ocr_engine is None:
        paddleocr = importlib.import_module("paddleocr")
        PaddleOCR = getattr(paddleocr, "PaddleOCR")
        ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")
    return ocr_engine


def _ocr_text_from_file(file_path: str) -> str:
    engine = _get_ocr_engine()
    result = engine.ocr(file_path, cls=True)
    parts: list[str] = []
    for block in result or []:
        for line in block or []:
            if len(line) >= 2 and isinstance(line[1], (list, tuple)) and line[1]:
                text = str(line[1][0]).strip()
                if text:
                    parts.append(text)
    return "\n".join(parts)


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def parse_uploaded_file(filename: str, content_bytes: bytes) -> dict:
    ext = Path(filename).suffix.lower()
    raw_text = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".tmp") as tmp:
        tmp.write(content_bytes)
        temp_path = tmp.name

    try:
        if ext in IMAGE_EXTS or ext == ".pdf":
            try:
                raw_text = _ocr_text_from_file(temp_path)
            except Exception:
                raw_text = content_bytes.decode("utf-8", errors="ignore")
        else:
            raw_text = content_bytes.decode("utf-8", errors="ignore")
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except OSError:
            pass

    raw_text = raw_text[:4000]
    doc_type = "form16" if ("form" in filename.lower() or "16" in filename.lower()) else "portfolio_statement"

    # Pass OCR text to LLM — no hallucination, missing fields stay null
    llm_fields = parse_ocr_to_structured_json(raw_text, doc_type)

    return {
        "document_type": doc_type,
        "extracted_fields": llm_fields,
        "raw_text_preview": raw_text[:1000],
        "source_ext": ext,
        "ocr_engine": "paddleocr",
    }
