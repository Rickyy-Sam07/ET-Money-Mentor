# [DEV1] upload_service.py — OCR + LLM structured parsing. Dev2: do not modify.
import importlib
import io
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from app.services.groq_service import parse_ocr_to_structured_json

ocr_engine: Any = None
logger = logging.getLogger(__name__)


def _get_ocr_engine() -> Any:
    global ocr_engine
    if ocr_engine is None:
        # Reduce startup checks/noise and keep runtime conservative on Windows CPU.
        os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")
        os.environ.setdefault("FLAGS_use_mkldnn", "0")

        paddleocr = importlib.import_module("paddleocr")
        PaddleOCR = getattr(paddleocr, "PaddleOCR")
        try:
            # Newer PaddleOCR versions replaced use_angle_cls with use_textline_orientation.
            ocr_engine = PaddleOCR(use_textline_orientation=True, lang="en")
        except TypeError:
            ocr_engine = PaddleOCR(use_angle_cls=True, lang="en")
    return ocr_engine


def _collect_text_parts(node: Any, out: list[str]) -> None:
    if node is None:
        return

    if isinstance(node, str):
        text = node.strip()
        if text:
            out.append(text)
        return

    if isinstance(node, dict):
        for key in ("text", "rec_text", "ocr_text"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                out.append(value.strip())
        rec_texts = node.get("rec_texts")
        if isinstance(rec_texts, list):
            for item in rec_texts:
                if isinstance(item, str) and item.strip():
                    out.append(item.strip())
        for value in node.values():
            _collect_text_parts(value, out)
        return

    if isinstance(node, (list, tuple)):
        # Legacy PaddleOCR format: [box, [text, score]]
        if len(node) >= 2 and isinstance(node[1], (list, tuple)) and node[1]:
            maybe_text = node[1][0]
            if isinstance(maybe_text, str) and maybe_text.strip():
                out.append(maybe_text.strip())
        for item in node:
            _collect_text_parts(item, out)
        return

    if hasattr(node, "to_dict"):
        try:
            _collect_text_parts(node.to_dict(), out)
            return
        except Exception:
            pass

    for attr in ("res", "result", "data"):
        if hasattr(node, attr):
            try:
                _collect_text_parts(getattr(node, attr), out)
                return
            except Exception:
                pass


def _ocr_text_from_file(file_path: str) -> str:
    engine = _get_ocr_engine()
    try:
        result = engine.ocr(file_path)
    except Exception as exc:
        err_text = str(exc)
        is_paddle_runtime_issue = (
            "ConvertPirAttribute2RuntimeAttribute" in err_text
            or "onednn_instruction" in err_text
            or "Unimplemented" in err_text
        )
        if not is_paddle_runtime_issue:
            raise

        logger.warning("Paddle runtime issue detected. Retrying OCR with compatibility flags.")
        # Retry in a safer mode for problematic Paddle CPU runtime combinations.
        os.environ["FLAGS_use_mkldnn"] = "0"
        os.environ["FLAGS_enable_pir_api"] = "0"
        os.environ["FLAGS_enable_pir_in_executor"] = "0"

        global ocr_engine
        ocr_engine = None
        engine = _get_ocr_engine()
        result = engine.ocr(file_path)

    # Fallback for API variants where ocr() returns minimal metadata.
    if (not result) and hasattr(engine, "predict"):
        try:
            result = engine.predict(
                file_path,
                use_doc_orientation_classify=True,
                use_textline_orientation=True,
            )
        except TypeError:
            result = engine.predict(file_path)

    parts: list[str] = []
    _collect_text_parts(result, parts)

    # Deduplicate while preserving order.
    unique_parts = list(dict.fromkeys(parts))
    return "\n".join(unique_parts)


IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}


def _detect_file_kind(filename: str, content_bytes: bytes) -> str:
    ext = Path(filename).suffix.lower()
    header = content_bytes[:16]

    if header.startswith(b"%PDF"):
        return "pdf"
    if header.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image"
    if header.startswith(b"\xff\xd8\xff"):
        return "image"
    if header.startswith(b"RIFF") and b"WEBP" in content_bytes[:64]:
        return "image"
    if header[:2] in {b"BM", b"II", b"MM"}:
        return "image"

    if ext == ".pdf":
        return "pdf"
    if ext in IMAGE_EXTS:
        return "image"
    return "text"


def _extract_pdf_text(content_bytes: bytes) -> str:
    try:
        pypdf = importlib.import_module("pypdf")
    except Exception:
        return ""

    try:
        PdfReader = getattr(pypdf, "PdfReader")
        reader = PdfReader(io.BytesIO(content_bytes))
        parts: list[str] = []
        for page in reader.pages:
            text = (page.extract_text() or "").strip()
            if text:
                parts.append(text)
        return "\n".join(parts).strip()
    except Exception:
        return ""


def _decode_text_bytes(content_bytes: bytes) -> str:
    text = content_bytes.decode("utf-8", errors="ignore")
    if not text:
        return ""

    sample = text[:1500]
    printable = sum(1 for ch in sample if ch.isprintable() or ch in "\n\r\t")
    ratio = printable / max(len(sample), 1)
    if ratio < 0.9:
        return ""

    return text


def parse_uploaded_file(filename: str, content_bytes: bytes) -> dict:
    ext = Path(filename).suffix.lower()
    file_kind = _detect_file_kind(filename, content_bytes)
    raw_text = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".tmp") as tmp:
        tmp.write(content_bytes)
        temp_path = tmp.name

    try:
        if file_kind == "pdf":
            # Prefer native text extraction for digital PDFs; OCR only if PDF has no text layer.
            raw_text = _extract_pdf_text(content_bytes)
            if not raw_text:
                try:
                    raw_text = _ocr_text_from_file(temp_path)
                except Exception:
                    logger.warning("OCR failed for uploaded file: %s", filename)
                    raw_text = ""
        elif file_kind == "image":
            try:
                raw_text = _ocr_text_from_file(temp_path)
            except Exception:
                logger.warning("OCR failed for uploaded file: %s", filename)
                raw_text = ""
        else:
            raw_text = _decode_text_bytes(content_bytes)
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except OSError:
            pass

    if not raw_text.strip() and file_kind in {"image", "pdf"}:
        raw_text = "Could not extract readable text from this file. Please upload a clearer scan or text-based document."

    raw_text = raw_text[:4000]
    doc_type = "form16" if ("form" in filename.lower() or "16" in filename.lower()) else "portfolio_statement"

    # Pass OCR text to LLM — no hallucination, missing fields stay null
    llm_fields = parse_ocr_to_structured_json(raw_text, doc_type)

    return {
        "document_type": doc_type,
        "extracted_fields": llm_fields,
        "raw_text_preview": raw_text[:1000],
        "source_ext": ext,
        "source_kind": file_kind,
        "ocr_engine": "paddleocr",
    }
