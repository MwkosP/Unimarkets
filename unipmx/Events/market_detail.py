"""Public Events API — market-scoped detail fetches."""

from __future__ import annotations

from typing import Any

from pmxt.models import OrderBook, Trade, UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, DEFAULT_LIMIT, ResolutionKey
from unipmx.models import Holder, MarketPosition, MarketRules, MarketStats, PricePoint, Resolution

from .helpers import (
    market_condition_id,
    market_stats_from,
    normalize_holder,
    normalize_position,
    normalize_trade,
    price_points_from_candles,
    price_points_from_history,
    primary_outcome_id,
    resolution_from,
    rules_from,
)
from .markets import fetchMarket
from .orderbook import fetchOrderBook
from .polymarket import call_polymarket
from .support import COMMENTS_VENUES, HOLDERS_VENUES, POSITIONS_VENUES


def _resolve_market(market_id: str, exchange: str) -> UnifiedMarket:
    return fetchMarket(market_id, exchange=exchange)


@spun()
def fetchMarketOrderBook(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> OrderBook:
    """Live order book for a market's primary active outcome."""
    market = _resolve_market(market_id, exchange)
    for outcome in market.outcomes:
        if 0.01 < outcome.price < 0.99:
            return fetchOrderBook(outcome.outcome_id, exchange=exchange, **kwargs)
    return fetchOrderBook(primary_outcome_id(market), exchange=exchange, **kwargs)


@spun()
def fetchMarketActivity(
    market_id: str,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> list[Trade]:
    """Recent trades for a market."""
    market = _resolve_market(market_id, exchange)
    client = getClient(exchange)

    if exchange == "Polymarket":
        condition = market_condition_id(market)
        raw = call_polymarket(
            client,
            "getTrades",
            {"market": condition, "limit": limit, **kwargs},
        )
        if isinstance(raw, list):
            return [normalize_trade(t, source=exchange) for t in raw[:limit]]
        return []

    return client.fetch_trades(primary_outcome_id(market), limit=limit, **kwargs)


@spun()
def fetchMarketTopHolders(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int = 20,
    **kwargs: Any,
) -> list[Holder]:
    """Largest position holders for a market."""
    if exchange not in HOLDERS_VENUES:
        return []

    market = _resolve_market(market_id, exchange)
    condition = market_condition_id(market)
    client = getClient(exchange)
    raw = call_polymarket(client, "getHolders", {"market": condition, "limit": limit, **kwargs})
    holders: list[Holder] = []
    if not isinstance(raw, list):
        return holders
    for group in raw:
        token = group.get("token")
        outcome = None
        for o in market.outcomes:
            if o.outcome_id == token:
                outcome = o.label
                break
        for row in group.get("holders") or []:
            holders.append(normalize_holder(row, outcome=outcome, source=exchange))
    return holders[:limit]


@spun()
def fetchMarketStats(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> MarketStats:
    """Aggregate stats: volume, liquidity, open interest."""
    market = _resolve_market(market_id, exchange)
    extra: dict | None = None

    if exchange == "Polymarket":
        condition = market_condition_id(market)
        try:
            oi = call_polymarket(getClient(exchange), "getOi", {"market": condition, **kwargs})
            if isinstance(oi, list) and oi:
                extra = oi[0]
        except Exception:
            pass

    return market_stats_from(market, exchange=exchange, extra=extra)


@spun()
def fetchMarketResolution(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> Resolution:
    """Resolution outcome and resolver metadata."""
    market = _resolve_market(market_id, exchange)
    return resolution_from(market, exchange=exchange)


@spun()
def fetchMarketRules(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> MarketRules:
    """Resolution rules / criteria for a market."""
    market = _resolve_market(market_id, exchange)
    return rules_from(market, exchange=exchange)


@spun()
def fetchMarketGraph(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    resolution: ResolutionKey = "1d",
    limit: int | None = None,
    **kwargs: Any,
) -> list[PricePoint]:
    """Price history suitable for charting (YES/NO timeseries)."""
    market = _resolve_market(market_id, exchange)
    client = getClient(exchange)
    outcome_id = primary_outcome_id(market)

    if exchange == "Polymarket":
        yes_id = outcome_id
        no_id = market.no.outcome_id if market.no else None
        interval = resolution if resolution != "max" else "max"
        yes_raw = call_polymarket(
            client,
            "getPricesHistory",
            {"market": yes_id, "interval": interval, **kwargs},
        )
        history = yes_raw.get("history", []) if isinstance(yes_raw, dict) else []
        no_history = None
        if no_id:
            try:
                no_raw = call_polymarket(
                    client,
                    "getPricesHistory",
                    {"market": no_id, "interval": interval, **kwargs},
                )
                no_history = no_raw.get("history", []) if isinstance(no_raw, dict) else []
            except Exception:
                pass
        points = price_points_from_history(history, no_history=no_history, source=exchange)
        if limit is not None:
            return points[-limit:]
        return points

    candles = client.fetch_ohlcv(
        outcome_id,
        resolution=resolution,
        limit=limit,
        **kwargs,
    )
    points = price_points_from_candles(candles, exchange=exchange)
    if limit is not None:
        return points[-limit:]
    return points


@spun()
def fetchMarketPositions(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int | None = None,
    **kwargs: Any,
) -> list[MarketPosition]:
    """All open positions in a market (aggregate, not per-user)."""
    if exchange not in POSITIONS_VENUES:
        return []

    market = _resolve_market(market_id, exchange)
    condition = market_condition_id(market)
    raw = call_polymarket(
        getClient(exchange),
        "getV1MarketPositions",
        {"market": condition, **kwargs},
    )
    positions: list[MarketPosition] = []
    if not isinstance(raw, list):
        return positions
    for group in raw:
        for row in group.get("positions") or []:
            pos = normalize_position(row, source=exchange)
            if pos.size > 0:
                positions.append(pos)
    if limit is not None:
        return positions[:limit]
    return positions
