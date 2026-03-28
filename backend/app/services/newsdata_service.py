# [DEV1] newsdata_service.py — NewsData.io live feed + sentiment. Dev2: do not modify.
import os = "https://newsdata.io/api/1/latest"
_CACHE: dict[str, Any] = {"expires_at": 0.0, "items": []}


def _get_with_retry(params: dict[str, Any]) -> dict[str, Any]:
    timeout_sec = int(os.getenv("NEWSDATA_TIMEOUT_SEC", "15"))
    max_attempts = int(os.getenv("NEWSDATA_MAX_RETRIES", "3"))
    backoff = 1.0

    last_error: Exception | None = None
    for attempt in range(max_attempts):
        try:
            response = requests.get(NEWSDATA_URL, params=params, timeout=timeout_sec)
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

    raise RuntimeError(f"NewsData request failed after retries: {last_error}")


def _normalize_items(raw: list[dict[str, Any]], max_items: int) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in raw[:max_items]:
        items.append(
            {
                "title": row.get("title") or "Untitled",
                "source": row.get("source_id") or "newsdata",
                "summary": row.get("description") or row.get("content") or "",
                "link": row.get("link"),
                "keywords": row.get("keywords") or [],
            }
        )
    return items


def fetch_latest_finance_news(max_items: int = 10) -> list[dict[str, Any]]:
    api_key = os.getenv("NEWSDATA_API_KEY")
    if not api_key:
        return []

    now = time.time()
    if _CACHE["expires_at"] > now:
        return list(_CACHE["items"])[:max_items]

    params = {
        "apikey": api_key,
        "language": "en",
        "category": "business",
        "country": "in",
    }

    try:
        payload = _get_with_retry(params=params)
        raw_items = payload.get("results") or []
        items = _normalize_items(raw_items, max_items)
        _CACHE["items"] = items
        _CACHE["expires_at"] = now + 600
        return items
    except Exception:
        return []


def market_sentiment(news_items: list[dict[str, Any]]) -> dict[str, Any]:
    if not news_items:
        return {"label": "neutral", "score": 0, "reason": "No live market signals available."}

    negative_tokens = {
        "fraud",
        "downgrade",
        "default",
        "crash",
        "probe",
        "penalty",
        "decline",
        "fall",
    }
    positive_tokens = {
        "rally",
        "gain",
        "growth",
        "upgrade",
        "surge",
        "record",
        "inflow",
        "beat",
    }

    score = 0
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        score += sum(1 for token in positive_tokens if token in text)
        score -= sum(1 for token in negative_tokens if token in text)

    if score >= 3:
        return {"label": "positive", "score": score, "reason": "Recent financial news flow is risk-on."}
    if score <= -3:
        return {"label": "negative", "score": score, "reason": "Recent financial news flow is risk-off."}
    return {"label": "neutral", "score": score, "reason": "Recent financial news is mixed."}
