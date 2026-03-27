import importlib
import re
import tempfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

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


def _extract_number(pattern: str, text: str, default: float) -> float:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return default
    raw = match.group(1).replace(",", "")
    try:
        return float(raw)
    except ValueError:
        return default


def _parse_date(value: str) -> str | None:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None


def _parse_portfolio_transactions(raw_text: str) -> list[dict[str, Any]]:
    # Best-effort parser for CAMS/KFin-like rows in OCR/text output.
    # Supported shape example:
    # 2023-01-10 | Fund Name | Amount 5000 | Units 120.5 | NAV 41.4
    rows: list[dict[str, Any]] = []
    amount_rx = re.compile(r"amount\s*[:=]?\s*([0-9,]+(?:\.[0-9]+)?)", flags=re.IGNORECASE)
    units_rx = re.compile(r"units?\s*[:=]?\s*([0-9,]+(?:\.[0-9]+)?)", flags=re.IGNORECASE)
    nav_rx = re.compile(r"nav\s*[:=]?\s*([0-9,]+(?:\.[0-9]+)?)", flags=re.IGNORECASE)

    for line in raw_text.splitlines():
        cleaned = line.strip()
        if not cleaned:
            continue

        date_match = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2}|[0-9]{2}[/-][0-9]{2}[/-][0-9]{4})", cleaned)
        date_iso = _parse_date(date_match.group(1)) if date_match else None

        amount_match = amount_rx.search(cleaned)
        units_match = units_rx.search(cleaned)
        nav_match = nav_rx.search(cleaned)

        if not (date_iso and amount_match and (units_match or nav_match)):
            continue

        amount = float(amount_match.group(1).replace(",", ""))
        units = float(units_match.group(1).replace(",", "")) if units_match else 0.0
        nav = float(nav_match.group(1).replace(",", "")) if nav_match else (amount / units if units else 0.0)

        name = "Unknown Fund"
        segments = [seg.strip() for seg in re.split(r"\||,", cleaned) if seg.strip()]
        for seg in segments:
            lower = seg.lower()
            if any(token in lower for token in ["amount", "units", "nav", "purchase", "sip"]):
                continue
            if re.search(r"[a-zA-Z]", seg):
                name = seg
                break

        rows.append(
            {
                "date": date_iso,
                "fund": name,
                "amount": amount,
                "units": units,
                "nav": nav,
            }
        )

    return rows


def _build_holdings_from_transactions(transactions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "name": "Unknown Fund",
            "units": 0.0,
            "nav": 0.0,
            "invested_amount": 0.0,
            "buy_date": None,
            "transactions": [],
        }
    )

    for tx in transactions:
        name = tx["fund"]
        row = grouped[name]
        row["name"] = name
        row["units"] += float(tx["units"])
        row["nav"] = float(tx["nav"])
        row["invested_amount"] += float(tx["amount"])
        if row["buy_date"] is None or tx["date"] < row["buy_date"]:
            row["buy_date"] = tx["date"]
        row["transactions"].append({"date": tx["date"], "amount": tx["amount"]})

    return list(grouped.values())


def parse_uploaded_file(filename: str, content_bytes: bytes) -> dict:
    ext = Path(filename).suffix.lower()
    sample_text = ""

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext or ".tmp") as tmp:
        tmp.write(content_bytes)
        temp_path = tmp.name

    try:
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".pdf"}:
            try:
                sample_text = _ocr_text_from_file(temp_path)[:3000]
            except Exception:
                # Fallback if OCR runtime/model setup is unavailable on host.
                sample_text = content_bytes.decode("utf-8", errors="ignore")[:3000]
        else:
            sample_text = content_bytes.decode("utf-8", errors="ignore")[:3000]
    finally:
        try:
            Path(temp_path).unlink(missing_ok=True)
        except OSError:
            pass

    if "form" in filename.lower() or "16" in filename.lower():
        gross_salary = _extract_number(r"gross\s*salary\D*([0-9,]+)", sample_text, 1200000)
        ded_80c = _extract_number(r"80c\D*([0-9,]+)", sample_text, 60000)
        ded_80d = _extract_number(r"80d\D*([0-9,]+)", sample_text, 12000)

        return {
            "document_type": "form16",
            "extracted_fields": {
                "employer": "Sample Employer Pvt Ltd",
                "gross_salary": gross_salary,
                "deductions_80c": ded_80c,
                "deductions_80d": ded_80d,
                "raw_text_preview": sample_text,
            },
            "source_ext": ext,
            "ocr_engine": "paddleocr",
        }

    parsed_transactions = _parse_portfolio_transactions(sample_text)
    parsed_holdings = _build_holdings_from_transactions(parsed_transactions) if parsed_transactions else []

    return {
        "document_type": "portfolio_statement",
        "extracted_fields": {
            "funds": parsed_holdings
            if parsed_holdings
            else [
                {"name": "Nifty Index Fund", "units": 250.0, "nav": 42.3, "invested_amount": 10000, "buy_date": "2023-01-10"},
                {"name": "Flexi Cap Fund", "units": 180.0, "nav": 66.2, "invested_amount": 9000, "buy_date": "2023-05-10"},
            ],
            "transactions_count": len(parsed_transactions),
            "raw_text_preview": sample_text,
        },
        "source_ext": ext,
        "ocr_engine": "paddleocr",
    }
