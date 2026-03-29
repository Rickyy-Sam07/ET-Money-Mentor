# [DEV1] news_service.py — RAG news query + warning tagging. Dev2: do not modify.
from typing import Any

from app.services.newsdata_service import fetch_latest_finance_news


NEWS_STORE = [
    {
        "title": "RBI maintains repo rate amid inflation watch",
        "source": "Economic Times",
        "summary": "RBI held rates steady while signaling data-dependent policy changes.",
        "tags": ["macro", "debt", "interest-rates"],
        "sentiment": "neutral",
    },
    {
        "title": "SEBI warns against unregistered advisory channels",
        "source": "Moneycontrol",
        "summary": "Investors advised to verify advisor registration before acting on tips.",
        "tags": ["regulation", "investor-safety", "warning"],
        "sentiment": "negative",
    },
    {
        "title": "Large-cap index funds see strong monthly inflows",
        "source": "ET Markets",
        "summary": "Passive large-cap funds continued to attract retail SIPs.",
        "tags": ["mutual-fund", "equity", "index"],
        "sentiment": "positive",
    },
]


def query_news(context: dict[str, Any]) -> list[dict[str, Any]]:
    live_items = fetch_latest_finance_news(max_items=10)
    store = live_items if live_items else NEWS_STORE
    holdings = " ".join([str(item.get("name", "")) for item in context.get("holdings", [])]).lower()

    results = []
    for item in store:
        tags = item.get("tags") or item.get("keywords") or []
        sentiment = item.get("sentiment", "neutral")
        warn = sentiment == "negative" or "warning" in tags
        impact = "Monitor closely." if warn else "No immediate action required."

        relevance = 0.6
        if "index" in holdings and "index" in tags:
            relevance = 0.92
        elif "debt" in holdings and "debt" in tags:
            relevance = 0.88

        row = {
            **item,
            "warning": warn,
            "impact": impact,
            "relevance": relevance,
            "is_live": bool(live_items),
        }
        results.append(row)

    return sorted(results, key=lambda x: x["relevance"], reverse=True)[:5]
