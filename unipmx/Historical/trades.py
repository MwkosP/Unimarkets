"""Public Historical API — market trade history."""

from __future__ import annotations

from datetime import datetime

from pmxt.models import Trade, UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE

from .utils import market_history_bounds


@spun()
def fetchTrades(
    outcome_id: str,
    *,
    limit: int | None = None,
    since: int | None = None,
    start: str | int | datetime | None = None,
    end: str | int | datetime | None = None,
    market: UnifiedMarket | None = None,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[Trade]:
    """
    Fetch trade history for an outcome.

    ``limit=None`` (default) requests the venue maximum per call.
    Pass ``market=`` to auto-fill ``start``/``end`` from metadata when omitted.
    """
    if market and start is None and end is None:
        meta_start, meta_end = market_history_bounds(market)
        start = meta_start.isoformat() if meta_start else None
        end = meta_end.isoformat() if meta_end else None

    kwargs: dict = {}
    if limit is not None:
        kwargs["limit"] = limit
    if since is not None:
        kwargs["since"] = since
    if start is not None:
        kwargs["start"] = start.isoformat() if isinstance(start, datetime) else start
    if end is not None:
        kwargs["end"] = end.isoformat() if isinstance(end, datetime) else end

    return getClient(exchange).fetch_trades(outcome_id, **kwargs)
