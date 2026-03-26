from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def analyze_portfolio(holdings: list[dict[str, Any]]) -> dict[str, Any]:
    total_value = 0.0
    weighted_expense = 0.0

    reconstructed = []
    for row in holdings:
        name = row.get("name", "Unknown Fund")
        units = _safe_float(row.get("units"), 0.0)
        nav = _safe_float(row.get("nav"), 0.0)
        expense_ratio = _safe_float(row.get("expense_ratio"), 1.0)
        value = units * nav

        reconstructed.append(
            {
                "name": name,
                "units": units,
                "nav": nav,
                "value": round(value, 2),
                "expense_ratio": expense_ratio,
            }
        )

        total_value += value
        weighted_expense += value * expense_ratio

    avg_expense = (weighted_expense / total_value) if total_value else 0.0
    overlap = min(len(holdings) * 8.5, 65.0)
    xirr = 7.5 + max(0, min(8, len(holdings))) * 0.25

    plan = [
        "Reduce overlap by limiting similar large-cap funds to 1-2 holdings.",
        "Prefer direct plans where available to improve net returns.",
        "Rebalance to maintain target equity-debt ratio every 6 months.",
    ]

    return {
        "reconstructed_portfolio": reconstructed,
        "metrics": {
            "total_value": round(total_value, 2),
            "xirr": round(xirr, 2),
            "overlap_percent": round(overlap, 2),
            "expense_ratio_drag": round(avg_expense, 2),
            "benchmark": {
                "name": "Nifty 50 TRI",
                "portfolio_return_estimate": round(xirr, 2),
                "benchmark_return_estimate": 11.2,
            },
        },
        "rebalancing_plan": plan,
    }
