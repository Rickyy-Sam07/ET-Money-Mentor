from pathlib import Path


def parse_uploaded_file(filename: str, content_bytes: bytes) -> dict:
    ext = Path(filename).suffix.lower()
    sample_text = content_bytes.decode("utf-8", errors="ignore")[:1200]

    if "form" in filename.lower() or "16" in filename.lower():
        return {
            "document_type": "form16",
            "extracted_fields": {
                "employer": "Sample Employer Pvt Ltd",
                "gross_salary": 1200000,
                "deductions_80c": 60000,
                "deductions_80d": 12000,
                "raw_text_preview": sample_text,
            },
            "source_ext": ext,
        }

    return {
        "document_type": "portfolio_statement",
        "extracted_fields": {
            "funds": [
                {"name": "Nifty Index Fund", "units": 250.0, "nav": 42.3},
                {"name": "Flexi Cap Fund", "units": 180.0, "nav": 66.2},
            ],
            "raw_text_preview": sample_text,
        },
        "source_ext": ext,
    }
