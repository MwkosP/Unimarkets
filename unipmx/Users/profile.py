"""Public Users API — user profile."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserProfile

from .polymarket import (
    as_float,
    get_json,
    normalize_position,
    normalize_profile,
    polymarket_supported,
)


def _profile_stats(address: str) -> dict:
    open_raw = get_json("https://data-api.polymarket.com", "/positions", {"user": address, "limit": 500})
    closed_raw = get_json("https://data-api.polymarket.com", "/closed-positions", {"user": address, "limit": 500})
    open_rows = open_raw if isinstance(open_raw, list) else []
    closed_rows = closed_raw if isinstance(closed_raw, list) else []
    positions = [
        *[normalize_position(address, row, status="open") for row in open_rows],
        *[normalize_position(address, row, status="closed") for row in closed_rows],
    ]

    value_raw = get_json("https://data-api.polymarket.com", "/value", {"user": address})
    if isinstance(value_raw, dict):
        positions_value = as_float(
            value_raw.get("value") or value_raw.get("total") or value_raw.get("portfolioValue")
        )
    else:
        positions_value = as_float(value_raw)
    if positions_value is None:
        positions_value = sum(p.current_value or 0 for p in positions if p.status == "open")

    wins = [p.cash_pnl for p in positions if p.cash_pnl is not None]
    realized_wins = [p.realized_pnl for p in positions if p.realized_pnl is not None]
    biggest_win = max([*wins, *realized_wins], default=None)
    realized = sum(p.realized_pnl or 0 for p in positions)
    unrealized = sum(p.cash_pnl or 0 for p in positions)
    profit_loss = realized + unrealized
    profit_loss_percent = (profit_loss / positions_value) if positions_value else None
    market_ids = {p.market_id for p in positions if p.market_id}

    return {
        "positions_value": positions_value,
        "biggest_win": biggest_win,
        "predictions": len(market_ids) or len(positions),
        "profit_loss": profit_loss,
        "profit_loss_percent": profit_loss_percent,
        "positions_raw": [p.raw for p in positions],
        "value_raw": value_raw,
    }


@spun()
def fetchUserProfile(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UserProfile | None:
    if not polymarket_supported(exchange):
        return None

    raw = get_json("https://gamma-api.polymarket.com", "/public-profile", {"address": address})
    if not isinstance(raw, dict):
        return None
    stats = _profile_stats(address)
    enriched = {**raw, "_stats": stats}
    return normalize_profile(
        address,
        enriched,
        positions_value=stats["positions_value"],
        biggest_win=stats["biggest_win"],
        predictions=stats["predictions"],
        profit_loss=stats["profit_loss"],
        profit_loss_percent=stats["profit_loss_percent"],
    )
