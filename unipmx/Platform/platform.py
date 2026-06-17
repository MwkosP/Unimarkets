"""Public Platform API — venue-wide metadata and health."""

from __future__ import annotations

from json import JSONDecodeError
from typing import Any
from urllib.error import HTTPError, URLError

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE, EXCHANGES
from unipmx.models import (
    PlatformCategory,
    PlatformFee,
    PlatformStats,
    PlatformStatus,
    PlatformVenue,
)
from unipmx.Users.polymarket import as_float, get_json

GAMMA_API = "https://gamma-api.polymarket.com"
DATA_API = "https://data-api.polymarket.com"


def _polymarket_only(exchange: str) -> bool:
    return exchange == "Polymarket"


def _rows(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [row for row in value if isinstance(row, dict)]
    if isinstance(value, dict):
        for key in ("data", "markets", "events", "tags"):
            nested = value.get(key)
            if isinstance(nested, list):
                return [row for row in nested if isinstance(row, dict)]
    return []


def _safe_get(base_url: str, path: str, params: dict[str, Any] | None = None) -> Any:
    try:
        return get_json(base_url, path, params)
    except (HTTPError, URLError, TimeoutError, OSError, JSONDecodeError):
        return None


def _market_sample(limit: int) -> list[dict[str, Any]]:
    return _rows(_safe_get(GAMMA_API, "/markets", {"limit": limit}) or [])


@spun()
def fetchPlatformStats(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sample_limit: int = 500,
) -> PlatformStats | None:
    if not _polymarket_only(exchange):
        return None

    markets = _market_sample(sample_limit)
    events = _rows(_safe_get(GAMMA_API, "/events", {"limit": sample_limit}) or [])
    volume = sum(as_float(m.get("volumeNum") or m.get("volume")) or 0 for m in markets)
    liquidity = sum(as_float(m.get("liquidityNum") or m.get("liquidity")) or 0 for m in markets)
    active = sum(1 for m in markets if m.get("active") is True and not m.get("closed"))
    closed = sum(1 for m in markets if m.get("closed") is True)

    return PlatformStats(
        venue=exchange,
        markets_sampled=len(markets),
        active_markets=active,
        closed_markets=closed,
        events_sampled=len(events),
        volume=volume,
        liquidity=liquidity,
        raw={"markets": markets, "events": events},
    )


@spun()
def fetchPlatformFees(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int = 20,
) -> list[PlatformFee]:
    if not _polymarket_only(exchange):
        return []

    markets = _market_sample(max(limit, 50))
    fees: list[PlatformFee] = []
    for market in markets:
        fees.append(
            PlatformFee(
                venue=exchange,
                market_id=str(market.get("id")) if market.get("id") is not None else None,
                title=market.get("question") or market.get("title"),
                fee=market.get("fee") or market.get("feeSchedule") or market.get("feeType"),
                maker_base_fee=as_float(market.get("makerBaseFee")),
                taker_base_fee=as_float(market.get("takerBaseFee")),
                raw=market,
            )
        )
        if len(fees) >= limit:
            break
    return fees


@spun()
def fetchPlatformCategories(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int = 50,
) -> list[PlatformCategory]:
    if not _polymarket_only(exchange):
        return []

    tags = _rows(_safe_get(GAMMA_API, "/tags", {"limit": limit}) or [])
    categories: list[PlatformCategory] = []
    for tag in tags[:limit]:
        label = tag.get("label") or tag.get("name") or tag.get("slug") or str(tag.get("id") or "")
        categories.append(
            PlatformCategory(
                id=str(tag.get("id")) if tag.get("id") is not None else None,
                label=label,
                slug=tag.get("slug"),
                count=int(tag["count"]) if str(tag.get("count", "")).isdigit() else None,
                raw=tag,
            )
        )
    return categories


@spun()
def fetchPlatformStatus(
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> PlatformStatus:
    if not _polymarket_only(exchange):
        return PlatformStatus(
            venue=exchange,
            ok=False,
            components={},
            source=exchange,
            raw={"supported": False},
        )

    gamma_ok = _safe_get(GAMMA_API, "/markets", {"limit": 1}) is not None
    tags_ok = _safe_get(GAMMA_API, "/tags", {"limit": 1}) is not None
    data_ok = _safe_get(DATA_API, "/trades", {"limit": 1}) is not None
    components = {"gamma": gamma_ok, "tags": tags_ok, "data_api": data_ok}
    return PlatformStatus(venue=exchange, ok=all(components.values()), components=components, raw=components)


@spun()
def fetchPlatformVenues(
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[PlatformVenue]:
    user_tracking = {"Polymarket"}
    return [
        PlatformVenue(
            name=name,
            supported=True,
            user_tracking=name in user_tracking,
            raw={"selected": name == exchange},
        )
        for name in EXCHANGES
    ]
