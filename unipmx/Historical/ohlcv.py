"""Public Historical API — OHLCV candles."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pmxt.models import UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import OhlcvFrame

from .utils import (
    cap_ohlcv_limit,
    candles_have_bodies,
    fetch_ohlcv_all,
    fetch_trades_all,
    market_history_bounds,
    trades_to_candles,
)

SourceKey = Literal["trades", "api"]


@spun()
def fetchOhlcv(
    outcome_id: str,
    *,
    resolution: str = "1h",
    limit: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    market: UnifiedMarket | None = None,
    source: SourceKey = "trades",
    exchange: str = DEFAULT_EXCHANGE,
) -> OhlcvFrame:
    """
    Fetch price candles for an outcome.

    Returns an :class:`OhlcvFrame` — ``display(frame)`` for table,
    ``plot(frame['ohlc'])`` for candlestick chart.

    **source="trades"** (default) builds real OHLC candles from trade ticks
    (proper bodies, wicks, doji, etc.). The venue OHLCV API often returns
    flat O=H=L=C bars with no visible candles.

    **source="api"** uses the venue OHLCV endpoint directly.

    **Resolutions:** ``1m`` ``5m`` ``15m`` ``1h`` ``4h`` ``1d`` ``max``

    Examples::

        fetchOhlcvByQuery("btc", resolution="1d", limit=None)   # full daily history
        fetchOhlcvByQuery("btc", resolution="1h", limit=168)    # last week hourly
    """
    client = getClient(exchange)

    if market and start is None and end is None and limit is None:
        meta_start, meta_end = market_history_bounds(market)
        start = meta_start
        end = meta_end

    if source == "trades":
        trade_end = end or datetime.now(timezone.utc)
        trade_start = start
        if limit is not None and trade_start is None:
            from .utils import resolution_window

            trade_start = trade_end - resolution_window(resolution, limit + 8)
        trades = fetch_trades_all(client, outcome_id, start=trade_start, end=trade_end)
        candles = trades_to_candles(
            trades, resolution, start=trade_start, end=trade_end, limit=limit
        )
        return OhlcvFrame(candles)

    if limit is None:
        candles = fetch_ohlcv_all(
            client,
            outcome_id,
            resolution=resolution,
            start=start,
            end=end,
        )
    else:
        candles = client.fetch_ohlcv(
            outcome_id,
            resolution=resolution,
            limit=cap_ohlcv_limit(resolution, limit),
            start=start,
            end=end,
        )

    if not candles_have_bodies(candles):
        trades = fetch_trades_all(client, outcome_id, start=start, end=end)
        built = trades_to_candles(trades, resolution, start=start, end=end, limit=limit)
        if built:
            candles = built

    return OhlcvFrame(candles)


@spun()
def fetchOhlcvByQuery(
    query: str,
    *,
    resolution: str = "1h",
    limit: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    source: SourceKey = "trades",
    exchange: str = DEFAULT_EXCHANGE,
    market_index: int = 0,
    outcome_index: int | None = None,
    active_only: bool = True,
) -> OhlcvFrame:
    """Resolve market/outcome from query, then fetch OHLCV (full history by default)."""
    from unipmx.Events import getOutcomeId

    market, outcome = getOutcomeId(
        query,
        exchange=exchange,
        market_index=market_index,
        outcome_index=outcome_index,
        active_only=active_only,
    )
    return fetchOhlcv(
        outcome.outcome_id,
        resolution=resolution,
        limit=limit,
        start=start,
        end=end,
        market=market,
        source=source,
        exchange=exchange,
    )


@spun()
def fetchOhlcvForMarket(
    market: UnifiedMarket,
    *,
    outcome_index: int = 0,
    resolution: str = "1h",
    limit: int | None = None,
    start: datetime | None = None,
    end: datetime | None = None,
    source: SourceKey = "trades",
    exchange: str = DEFAULT_EXCHANGE,
) -> OhlcvFrame:
    """
    Fetch OHLCV for a market you already have (live or closed).

    ``end`` defaults to now for active markets, or ``closedTime`` when resolved.
    """
    outcome = market.outcomes[outcome_index]
    return fetchOhlcv(
        outcome.outcome_id,
        resolution=resolution,
        limit=limit,
        start=start,
        end=end,
        market=market,
        source=source,
        exchange=exchange,
    )
