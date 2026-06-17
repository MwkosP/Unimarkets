"""Polymarket public user-tracking endpoints."""

from __future__ import annotations

import json
import ssl
from typing import Any
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from unipmx.models import (
    UserActivityItem,
    UserLeaderboardEntry,
    UserMarket,
    UserPnL,
    UserPortfolioValue,
    UserPosition,
    UserProfile,
    UserRank,
    UserTradeRecord,
)

DATA_API = "https://data-api.polymarket.com"
GAMMA_API = "https://gamma-api.polymarket.com"


def polymarket_supported(exchange: str) -> bool:
    return exchange == "Polymarket"


def get_json(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    query = urlencode({k: v for k, v in (params or {}).items() if v is not None})
    url = f"{base_url}{path}"
    if query:
        url = f"{url}?{query}"
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "unipmx/0.1"})
    def parse(body: bytes) -> Any:
        text = body.decode("utf-8")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Polymarket returned a non-JSON response. The API may be blocked by "
                "your network/region, behind a VPN/captive page, or temporarily unavailable."
            ) from exc

    try:
        with urlopen(req, timeout=20) as res:
            return parse(res.read())
    except URLError as exc:
        reason = getattr(exc, "reason", None)
        if not isinstance(reason, ssl.SSLError):
            raise
        context = ssl._create_unverified_context()
        with urlopen(req, timeout=20, context=context) as res:
            return parse(res.read())


def as_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def as_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_profile(
    address: str,
    raw: dict[str, Any],
    *,
    positions_value: float | None = None,
    biggest_win: float | None = None,
    predictions: int | None = None,
    profit_loss: float | None = None,
    profit_loss_percent: float | None = None,
) -> UserProfile:
    return UserProfile(
        address=address,
        name=raw.get("name"),
        pseudonym=raw.get("pseudonym"),
        bio=raw.get("bio"),
        profile_image=raw.get("profileImage") or raw.get("profileImageOptimized"),
        x_username=raw.get("xUsername"),
        verified=raw.get("verifiedBadge"),
        joined_at=raw.get("createdAt") or raw.get("created_at") or raw.get("joinedAt"),
        views=as_int(raw.get("views") or raw.get("viewCount")),
        positions_value=positions_value,
        biggest_win=biggest_win,
        predictions=predictions,
        profit_loss=profit_loss,
        profit_loss_percent=profit_loss_percent,
        raw=raw,
    )


def normalize_position(address: str, raw: dict[str, Any], *, status: str | None) -> UserPosition:
    return UserPosition(
        user_address=address,
        market_id=raw.get("conditionId") or raw.get("market") or raw.get("marketId"),
        title=raw.get("title"),
        outcome=raw.get("outcome"),
        size=as_float(raw.get("size")) or 0.0,
        avg_price=as_float(raw.get("avgPrice")),
        current_price=as_float(raw.get("curPrice")),
        current_value=as_float(raw.get("currentValue")),
        cash_pnl=as_float(raw.get("cashPnl")),
        percent_pnl=as_float(raw.get("percentPnl")),
        realized_pnl=as_float(raw.get("realizedPnl")),
        status=status,
        raw=raw,
    )


def normalize_trade(address: str, raw: dict[str, Any]) -> UserTradeRecord:
    return UserTradeRecord(
        user_address=address,
        market_id=raw.get("conditionId") or raw.get("market") or raw.get("marketId"),
        title=raw.get("title"),
        outcome=raw.get("outcome"),
        side=(raw.get("side") or "").lower() or None,
        price=as_float(raw.get("price")),
        size=as_float(raw.get("size")),
        timestamp=as_int(raw.get("timestamp")),
        transaction_hash=raw.get("transactionHash"),
        raw=raw,
    )


def normalize_activity(address: str, raw: dict[str, Any]) -> UserActivityItem:
    return UserActivityItem(
        user_address=address,
        activity_type=raw.get("type") or raw.get("activityType"),
        market_id=raw.get("conditionId") or raw.get("market") or raw.get("marketId"),
        title=raw.get("title"),
        outcome=raw.get("outcome"),
        side=(raw.get("side") or "").lower() or None,
        price=as_float(raw.get("price")),
        size=as_float(raw.get("size")),
        timestamp=as_int(raw.get("timestamp")),
        raw=raw,
    )


def normalize_leaderboard(raw: dict[str, Any]) -> UserLeaderboardEntry:
    return UserLeaderboardEntry(
        rank=as_int(raw.get("rank")),
        user_address=raw.get("proxyWallet") or raw.get("address"),
        username=raw.get("userName") or raw.get("name") or raw.get("pseudonym"),
        volume=as_float(raw.get("vol") or raw.get("volume")),
        pnl=as_float(raw.get("pnl") or raw.get("profit")),
        profile_image=raw.get("profileImage"),
        x_username=raw.get("xUsername"),
        verified=raw.get("verifiedBadge"),
        raw=raw,
    )


def sort_positions(items: list[UserPosition], sort: str | None) -> list[UserPosition]:
    if sort in (None, "value"):
        return sorted(items, key=lambda p: p.current_value or 0, reverse=True)
    if sort in ("pnl", "profit"):
        return sorted(items, key=lambda p: p.cash_pnl or 0, reverse=True)
    if sort == "size":
        return sorted(items, key=lambda p: p.size, reverse=True)
    if sort == "title":
        return sorted(items, key=lambda p: (p.title or "").lower())
    return items


def sort_trades(items: list[UserTradeRecord], sort: str | None) -> list[UserTradeRecord]:
    if sort in (None, "newest"):
        return sorted(items, key=lambda t: t.timestamp or 0, reverse=True)
    if sort == "oldest":
        return sorted(items, key=lambda t: t.timestamp or 0)
    if sort == "size":
        return sorted(items, key=lambda t: t.size or 0, reverse=True)
    return items


def leaderboard_params(limit: int, window: str, by: str) -> dict[str, Any]:
    return {
        "limit": limit,
        "period": window,
        "timePeriod": window,
        "sortBy": by,
    }


def fetch_leaderboard(limit: int, window: str, by: str) -> list[UserLeaderboardEntry]:
    raw = get_json(DATA_API, "/v1/leaderboard", leaderboard_params(limit, window, by))
    rows = raw.get("leaderboard") if isinstance(raw, dict) else raw
    if not isinstance(rows, list):
        return []
    entries = [normalize_leaderboard(row) for row in rows[:limit]]
    if by in ("profit", "pnl"):
        return sorted(entries, key=lambda e: e.pnl or 0, reverse=True)[:limit]
    if by in ("volume", "vol"):
        return sorted(entries, key=lambda e: e.volume or 0, reverse=True)[:limit]
    return entries


def aggregate_pnl(address: str, window: str, positions: list[UserPosition]) -> UserPnL:
    realized = sum(p.realized_pnl or 0 for p in positions)
    unrealized = sum(p.cash_pnl or 0 for p in positions)
    total = realized + unrealized
    value = sum(p.current_value or 0 for p in positions)
    percent = (total / value) if value else None
    return UserPnL(
        user_address=address,
        window=window,
        realized=realized,
        unrealized=unrealized,
        total=total,
        percent=percent,
        raw={"positions": [p.raw for p in positions]},
    )
