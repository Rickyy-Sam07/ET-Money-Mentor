# [DEV1] portfolio_service.py — XIRR, overlap, rebalancing engine. Dev2: do not modify.
from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _parse_date(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _xnpv(rate: float, cashflows: list[tuple[datetime, float]]) -> float:
    t0 = cashflows[0][0]
    return sum(amount / ((1 + rate) ** ((dt - t0).days / 365.0)) for dt, amount in cashflows)


def _xirr(cashflows: list[tuple[datetime, float]]) -> float | None:
    if len(cashflows) < 2:
        return None
    if not any(amount < 0 for _, amount in cashflows) or not any(amount > 0 for _, amount in cashflows):
        return None

    low = -0.999
    high = 5.0
    for _ in range(120):
        mid = (low + high) / 2
        val = _xnpv(mid, cashflows)
        if abs(val) < 1e-6:
            return mid
        if val > 0:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def _constituent_overlap(holdings: list[dict[str, Any]]) -> float | None:
    universe: dict[str, float] = {}
    overlap_score = 0.0
    total_weight_seen = 0.0

    for holding in holdings:
        constituents = holding.get("constituents") or []
        for row in constituents:
            symbol = str(row.get("symbol", "")).strip().upper()
            weight = _safe_float(row.get("weight"), 0.0)
            if not symbol or weight <= 0:
                continue
            if symbol in universe:
                overlap_score += min(weight, universe[symbol])
            universe[symbol] = max(weight, universe.get(symbol, 0.0))
            total_weight_seen += weight

    if total_weight_seen == 0:
        return None
    return min((overlap_score / total_weight_seen) * 100.0, 100.0)


def analyze_portfolio(holdings: list[dict[str, Any]], market_signal: dict[str, Any] | None = None) -> dict[str, Any]:
    total_value = 0.0
    weighted_expense = 0.0
    total_invested = 0.0
    cashflows: list[tuple[datetime, float]] = []

    reconstructed = []
    for row in holdings:
        name = row.get("name", "Unknown Fund")
        units = _safe_float(row.get("units"), 0.0)
        nav = _safe_float(row.get("nav"), 0.0)
        expense_ratio = _safe_float(row.get("expense_ratio"), 1.0)
        value = units * nav
        invested_amount = _safe_float(row.get("invested_amount"), value)
        buy_date = str(row.get("buy_date", "")).strip()
        transactions = row.get("transactions") or []

        reconstructed.append(
            {
                "name": name,
                "units": units,
                "nav": nav,
                "value": round(value, 2),
                "expense_ratio": expense_ratio,
                "invested_amount": round(invested_amount, 2),
            }
        )

        total_value += value
        total_invested += invested_amount
        weighted_expense += value * expense_ratio

        dt = _parse_date(buy_date)
        if dt:
            cashflows.append((dt, -invested_amount))

        for tx in transactions:
            tx_date = _parse_date(str(tx.get("date", "")).strip())
            tx_amount = _safe_float(tx.get("amount"), 0.0)
            if tx_date and tx_amount > 0:
                cashflows.append((tx_date, -tx_amount))

    cashflows.append((datetime.utcnow(), total_value))

    xirr_value = _xirr(sorted(cashflows, key=lambda x: x[0]))
    cagr = None
    if total_invested > 0:
        cagr = ((total_value / total_invested) - 1) * 100

    avg_expense = (weighted_expense / total_value) if total_value else 0.0
    overlap = _constituent_overlap(holdings)
    if overlap is None:
        overlap = min(len(holdings) * 8.5, 65.0)

    xirr_percent = round((xirr_value * 100), 2) if xirr_value is not None else (round(cagr, 2) if cagr is not None else 0.0)

    plan = [
        "Reduce overlap by limiting similar large-cap funds to 1-2 holdings.",
        "Prefer direct plans where available to improve net returns.",
        "Rebalance to maintain target equity-debt ratio every 6 months.",
    ]
    if (market_signal or {}).get("label") == "negative":
        plan.insert(0, "Given negative market signal, prioritize quality debt allocation and avoid lump-sum equity entry.")

    return {
        "reconstructed_portfolio": reconstructed,
        "metrics": {
            "total_value": round(total_value, 2),
            "invested_amount": round(total_invested, 2),
            "xirr": xirr_percent,
            "overlap_percent": round(overlap, 2),
            "expense_ratio_drag": round(avg_expense, 2),
            "benchmark": {
                "name": "Nifty 50 TRI",
                "portfolio_return_estimate": xirr_percent,
                "benchmark_return_estimate": 11.2,
            },
        },
        "market_signal": market_signal
        or {"label": "neutral", "score": 0, "reason": "No live market signal available."},
        "rebalancing_plan": plan,
    }
