"""Public Users API — infer a user's trading style from existing user endpoints."""

from __future__ import annotations

from collections import Counter
from statistics import mean
from typing import Any

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserStyle

from .activity import fetchUserActivity
from .markets import fetchUserMarkets
from .pnl import fetchUserPnL, fetchUserRank
from .polymarket import polymarket_supported
from .portfolio import fetchUserPortfolioValue
from .positions import fetchUserPositions
from .profile import fetchUserProfile
from .trades import fetchUserTrades
from .wallet import fetchUserWalletAge


def _safe(label: str, fn, fallback: Any, errors: list[str]) -> Any:
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - keep style inference best-effort.
        errors.append(f"{label}: {exc}")
        return fallback


@spun()
def findUserStyle(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    trade_limit: int = 50,
    position_limit: int = 25,
    market_limit: int = 25,
    activity_limit: int = 25,
) -> UserStyle | None:
    if not polymarket_supported(exchange):
        return None

    errors: list[str] = []
    profile = _safe("profile", lambda: fetchUserProfile(address, exchange=exchange), None, errors)
    wallet_age = _safe("wallet age", lambda: fetchUserWalletAge(address, exchange=exchange), None, errors)
    portfolio = _safe("portfolio", lambda: fetchUserPortfolioValue(address, exchange=exchange), None, errors)
    pnl = _safe("PnL", lambda: fetchUserPnL(address, window="all", exchange=exchange), None, errors)
    rank = _safe(
        "rank",
        lambda: fetchUserRank(address, window="all", by="profit", exchange=exchange),
        None,
        errors,
    )
    positions = _safe(
        "positions",
        lambda: fetchUserPositions(
            address,
            status="open",
            sort="value",
            limit=position_limit,
            exchange=exchange,
        ),
        [],
        errors,
    )
    trades = _safe(
        "trades",
        lambda: fetchUserTrades(address, sort="newest", limit=trade_limit, exchange=exchange),
        [],
        errors,
    )
    activity = _safe(
        "activity",
        lambda: fetchUserActivity(address, limit=activity_limit, exchange=exchange),
        [],
        errors,
    )
    markets = _safe(
        "markets",
        lambda: fetchUserMarkets(address, status="open", limit=market_limit, exchange=exchange),
        [],
        errors,
    )

    trade_sides = Counter((trade.side or "unknown").lower() for trade in trades)
    outcomes = Counter((trade.outcome or "unknown").lower() for trade in trades)
    position_values = [position.current_value or 0 for position in positions]
    position_pnls = [position.cash_pnl for position in positions if position.cash_pnl is not None]
    market_titles = [market.title or "" for market in markets]

    total_trades = len(trades)
    open_value = sum(position_values)
    avg_position = mean(position_values) if position_values else 0
    biggest_position = max(position_values) if position_values else 0
    profitable_positions = sum(1 for value in position_pnls if value > 0)
    losing_positions = sum(1 for value in position_pnls if value < 0)

    if total_trades >= 50:
        activity_style = "very active"
    elif total_trades >= 15:
        activity_style = "active"
    elif total_trades > 0:
        activity_style = "selective"
    else:
        activity_style = "inactive / no recent trades"

    if biggest_position >= avg_position * 3 and len(position_values) >= 3:
        sizing_style = "concentrated sizing"
    elif len(position_values) >= 8:
        sizing_style = "diversified across many markets"
    else:
        sizing_style = "focused on a few markets"

    buy_count = trade_sides.get("buy", 0)
    sell_count = trade_sides.get("sell", 0)
    if buy_count > sell_count * 2:
        flow_style = "mostly enters positions"
    elif sell_count > buy_count:
        flow_style = "often exits or trims positions"
    else:
        flow_style = "balanced buying and selling"

    yes_count = outcomes.get("yes", 0)
    no_count = outcomes.get("no", 0)
    if yes_count > no_count * 1.5:
        directional_style = "leans YES"
    elif no_count > yes_count * 1.5:
        directional_style = "leans NO"
    else:
        directional_style = "mixed YES/NO"

    keywords = Counter()
    for title in market_titles:
        for word in title.lower().replace("?", "").replace(",", "").split():
            if len(word) >= 5:
                keywords[word] += 1

    data_available = bool(profile or wallet_age or portfolio or pnl or rank or positions or trades or activity or markets)
    if not data_available:
        activity_style = "unavailable"
        sizing_style = "unavailable"
        directional_style = "unavailable"
        flow_style = "unavailable"

    trader_type = f"{activity_style}, {sizing_style}, {directional_style}"
    return UserStyle(
        user_address=address,
        trader_type=trader_type,
        activity_style=activity_style,
        sizing_style=sizing_style,
        directional_style=directional_style,
        flow_style=flow_style,
        recent_trades=total_trades,
        open_markets=len(markets),
        open_position_value=open_value,
        average_position_value=avg_position,
        biggest_position_value=biggest_position,
        profitable_positions=profitable_positions,
        losing_positions=losing_positions,
        total_pnl=getattr(pnl, "total", None),
        pnl_percent=getattr(pnl, "percent", None),
        rank=getattr(rank, "rank", None),
        preferred_keywords=[word for word, _ in keywords.most_common(5)],
        data_available=data_available,
        errors=errors or None,
        raw={
            "profile": profile,
            "wallet_age": wallet_age,
            "portfolio": portfolio,
            "pnl": pnl,
            "rank": rank,
            "positions": positions,
            "trades": trades,
            "activity": activity,
            "markets": markets,
        },
    )
