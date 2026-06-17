"""Public Users API — wallet/profile age."""

from __future__ import annotations

from datetime import datetime, timezone

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserWalletAge, UserWalletConnection

from .polymarket import get_json, polymarket_supported


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


@spun()
def fetchUserWalletAge(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UserWalletAge | None:
    if not polymarket_supported(exchange):
        return None

    raw = get_json("https://gamma-api.polymarket.com", "/public-profile", {"address": address})
    if not isinstance(raw, dict):
        return None

    joined_at = raw.get("createdAt") or raw.get("created_at") or raw.get("joinedAt")
    joined = _parse_dt(joined_at)
    days = None
    years = None
    if joined:
        if joined.tzinfo is None:
            joined = joined.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - joined
        days = max(0, delta.days)
        years = round(days / 365.25, 2)

    return UserWalletAge(
        user_address=address,
        joined_at=joined_at,
        days=days,
        years=years,
        raw=raw,
    )


@spun()
def fetchUserWalletConnections(
    address: str,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserWalletConnection]:
    if not polymarket_supported(exchange):
        return []

    raw = get_json("https://gamma-api.polymarket.com", "/public-profile", {"address": address})
    if not isinstance(raw, dict):
        return []

    rows = raw.get("users") or raw.get("walletConnections") or raw.get("connections") or []
    if not isinstance(rows, list):
        return []

    connections: list[UserWalletConnection] = []
    for row in rows[:limit]:
        if not isinstance(row, dict):
            continue
        connections.append(
            UserWalletConnection(
                user_address=address,
                connection_id=str(row.get("id")) if row.get("id") is not None else row.get("address"),
                creator=row.get("creator"),
                mod=row.get("mod"),
                community_mod=row.get("communityMod"),
                raw=row,
            )
        )
    return connections
