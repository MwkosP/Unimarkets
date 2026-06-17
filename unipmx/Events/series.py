"""Public Events API — series (REST)."""

from typing import Any

from pmxt.models import UnifiedEvent, UnifiedMarket, UnifiedSeries

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, DEFAULT_LIMIT, SortKey, StatusKey
from unipmx.exceptions import BadRequest, NotFoundError
from unipmx.models import SeriesList

from .kalshi import fetch_series_events, fetch_series_markets
from .support import ensure_supported
from .utils import sort_markets


def _fetch_series(exchange: str, series_id: str, **kwargs: Any) -> UnifiedSeries:
    """Fetch one series by venue id; resolves slug/ticker/title when needed."""
    client = getClient(exchange)
    list_kwargs = {k: v for k, v in kwargs.items() if k != "id"}

    try:
        series_list = client.fetch_series(id=series_id, **list_kwargs)
        if series_list:
            return series_list[0]
    except BadRequest:
        pass

    needle = series_id.lower().replace("_", "-")
    for series in client.fetch_series(limit=200, **list_kwargs):
        haystack = {
            (series.id or "").lower(),
            (series.slug or "").lower(),
            (series.ticker or "").lower(),
            (series.title or "").lower(),
        }
        if needle in haystack:
            resolved = client.fetch_series(id=series.id, **list_kwargs)
            return resolved[0] if resolved else series

    raise NotFoundError(f"Series {series_id!r} not found on {exchange}")


def _series_events(series: UnifiedSeries, exchange: str, **kwargs: Any) -> list[UnifiedEvent]:
    if series.events:
        return list(series.events)
    client = getClient(exchange)
    if exchange == "Kalshi":
        return fetch_series_events(client, series, **kwargs)
    return []


def _series_markets(series: UnifiedSeries, exchange: str, **kwargs: Any) -> list[UnifiedMarket]:
    markets: list[UnifiedMarket] = []
    client = getClient(exchange)

    if exchange == "Kalshi":
        return fetch_series_markets(client, series, **kwargs)

    for event in series.events or []:
        if event.markets:
            markets.extend(event.markets)
        elif event.id:
            markets.extend(client.fetch_markets(event_id=event.id, limit=100, **kwargs))
    return markets


@spun()
def fetchSeries(
    query: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = "title",
    status: StatusKey | None = None,
    show_events: bool = True,
    show_markets: bool = True,
    **kwargs: Any,
) -> SeriesList:
    ensure_supported(exchange, "fetchSeries")
    params: dict = {"limit": limit, **kwargs}
    if query:
        params["query"] = query
    if status:
        params["status"] = status
    series = getClient(exchange).fetch_series(**params)
    if sort == "title":
        series = sorted(series, key=lambda s: s.title.lower())
    return SeriesList(series, show_events=show_events, show_markets=show_markets)


@spun()
def fetchSeriesMarkets(
    series_id: str,
    status: StatusKey | None = None,
    sort: SortKey | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> list[UnifiedMarket]:
    ensure_supported(exchange, "fetchSeriesMarkets")
    series = _fetch_series(exchange, series_id, **kwargs)
    markets = _series_markets(series, exchange, **kwargs)
    if status:
        markets = [m for m in markets if (m.status or "active") == status]
    markets = sort_markets(markets, sort)
    return markets[:limit]


@spun()
def fetchSeriesEvents(
    series_id: str,
    status: StatusKey | None = None,
    sort: SortKey | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> list[UnifiedEvent]:
    ensure_supported(exchange, "fetchSeriesEvents")
    series = _fetch_series(exchange, series_id, **kwargs)
    events = _series_events(series, exchange, limit=limit, **kwargs)
    if status:
        events = [e for e in events if _event_status(e) == status]
    if sort == "title":
        events = sorted(events, key=lambda e: e.title.lower())
    return events[:limit]


def _event_status(event: UnifiedEvent) -> str:
    meta = event.source_metadata or {}
    if meta.get("closed"):
        return "closed"
    if meta.get("active"):
        return "active"
    if meta.get("status") in ("closed", "settled", "finalized"):
        return "closed"
    if meta.get("status") in ("open", "active", "initialized"):
        return "active"
    return "all"
