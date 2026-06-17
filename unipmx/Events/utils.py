"""Internal helpers for Events module."""

from collections.abc import Callable
from typing import Any, TypeVar

from pmxt.models import UnifiedEvent, UnifiedMarket, UnifiedSeries

from unipmx.Display.utils import loading
from unipmx.config import API_SORT_KEYS, EXCHANGES, SortKey, StatusKey
from unipmx.models import EventResult, MarketResult, SeriesResult

T = TypeVar("T")


def outcome_price(market: UnifiedMarket, labels: tuple[str, ...]) -> float | None:
    for outcome in market.outcomes:
        if outcome.label.lower() in labels:
            return outcome.price
    return None


def market_to_result(exchange: str, market: UnifiedMarket) -> MarketResult:
    return MarketResult(
        exchange=exchange,
        title=market.title,
        yes_price=outcome_price(market, ("yes", "y")),
        no_price=outcome_price(market, ("no", "n")),
        volume=getattr(market, "volume", None) or market.volume_24h,
        market_id=market.market_id,
        url=market.url,
    )


def event_to_result(exchange: str, event: UnifiedEvent) -> EventResult:
    return EventResult(
        exchange=exchange,
        title=event.title,
        market_count=len(event.markets),
        volume=event.volume,
        event_id=event.id,
        url=event.url,
    )


def series_to_result(exchange: str, series: UnifiedSeries) -> SeriesResult:
    return SeriesResult(
        exchange=exchange,
        title=series.title,
        series_id=series.id,
        recurrence=series.recurrence,
        url=series.url,
    )


def _market_volume(market: UnifiedMarket) -> float:
    return market.volume or market.volume_24h or 0


def sort_markets(markets: list[UnifiedMarket], sort: SortKey | None) -> list[UnifiedMarket]:
    if not sort:
        return markets
    if sort == "volume":
        return sorted(markets, key=_market_volume, reverse=True)
    if sort == "liquidity":
        return sorted(markets, key=lambda m: m.liquidity or 0, reverse=True)
    if sort == "newest":
        return sorted(markets, key=lambda m: m.market_id or "", reverse=True)
    if sort == "title":
        return sorted(markets, key=lambda m: m.title.lower())
    return markets


def sort_events(events: list[UnifiedEvent], sort: SortKey | None) -> list[UnifiedEvent]:
    if not sort:
        return events
    if sort == "volume":
        return sorted(events, key=lambda e: e.volume or 0, reverse=True)
    if sort == "liquidity":
        return sorted(events, key=lambda e: e.volume_24h or e.volume or 0, reverse=True)
    if sort == "market_count":
        return sorted(events, key=lambda e: len(e.markets), reverse=True)
    if sort == "title":
        return sorted(events, key=lambda e: e.title.lower())
    if sort == "newest":
        return sorted(events, key=lambda e: e.id or "", reverse=True)
    return events


def sort_market_results(items: list[MarketResult], sort: SortKey | None) -> list[MarketResult]:
    if not sort:
        return items
    if sort == "volume":
        return sorted(items, key=lambda r: r.volume or 0, reverse=True)
    if sort == "title":
        return sorted(items, key=lambda r: r.title.lower())
    return items


def sort_event_results(items: list[EventResult], sort: SortKey | None) -> list[EventResult]:
    if not sort:
        return items
    if sort == "volume":
        return sorted(items, key=lambda r: r.volume or 0, reverse=True)
    if sort == "market_count":
        return sorted(items, key=lambda r: r.market_count, reverse=True)
    if sort == "title":
        return sorted(items, key=lambda r: r.title.lower())
    return items


def sort_series_results(items: list[SeriesResult], sort: SortKey | None) -> list[SeriesResult]:
    if not sort or sort == "title":
        return sorted(items, key=lambda r: r.title.lower())
    return items


def fetch_kwargs(
    query: str,
    limit: int,
    sort: SortKey | None = None,
    *,
    status: StatusKey | None = None,
) -> dict:
    params: dict = {"query": query, "limit": limit}
    if sort and sort in API_SORT_KEYS:
        params["sort"] = sort
    if status:
        params["status"] = status
    return params


def search_exchanges(
    query: str,
    limit: int,
    fetch_one,
    map_one: Callable[[str, Any], T],
    *,
    label: str = "markets",
    sort: SortKey | None = None,
    exchanges: tuple[str, ...] | None = None,
    on_error: Callable[[str], None] | None = print,
) -> list[T]:
    venues = exchanges or tuple(EXCHANGES.keys())
    results: list[T] = []
    with loading(f"Searching {label} for '{query}'…") as status:
        for name in venues:
            status.update(f"[cyan]{name}[/cyan]  fetching {label}…")
            try:
                for item in fetch_one(name):
                    results.append(map_one(name, item))
            except Exception as exc:
                if on_error:
                    on_error(f"  ⚠️  {name}: {exc}")
    return results
