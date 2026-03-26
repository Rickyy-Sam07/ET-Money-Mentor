from typing import Any


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
    holdings = " ".join([str(item.get("name", "")) for item in context.get("holdings", [])]).lower()

    results = []
    for item in NEWS_STORE:
        warn = item["sentiment"] == "negative" or "warning" in item["tags"]
        impact = "Monitor closely." if warn else "No immediate action required."

        relevance = 0.6
        if "index" in holdings and "index" in item["tags"]:
            relevance = 0.92
        elif "debt" in holdings and "debt" in item["tags"]:
            relevance = 0.88

        row = {
            **item,
            "warning": warn,
            "impact": impact,
            "relevance": relevance,
        }
        results.append(row)

    return sorted(results, key=lambda x: x["relevance"], reverse=True)[:5]
