"""Cross-venue client — same fetch* API as venue clients, fans out to all exchanges."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pmxt

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_LIMIT, EXCHANGES, SortKey, StatusKey
from unipmx.Events.events import fetchEvents
from unipmx.Events.markets import fetchMarkets
from unipmx.Events.series import fetchSeries
from unipmx.Events.utils import (
    event_to_result,
    market_to_result,
    search_exchanges,
    series_to_result,
    sort_event_results,
    sort_market_results,
    sort_series_results,
)
from unipmx.models import SearchResults


class All:
    """Query every venue (or a subset) with the same API as :class:`Polymarket`."""

    def __init__(
        self,
        exchanges: tuple[str, ...] | None = None,
        *,
        on_error: Callable[[str], None] | None = print,
    ) -> None:
        self.exchanges = exchanges or tuple(EXCHANGES.keys())
        self.on_error = on_error

    @property
    def name(self) -> str:
        return "All"

    @spun("Searching all markets…")
    def fetchMarkets(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = "volume",
        status: StatusKey | None = None,
    ) -> SearchResults:
        items = search_exchanges(
            query,
            limit,
            lambda name: fetchMarkets(query, limit, exchange=name, sort=sort, status=status),
            market_to_result,
            label="markets",
            sort=sort,
            exchanges=self.exchanges,
            on_error=self.on_error,
        )
        items = sort_market_results(items, sort)
        return SearchResults(query=query, limit=limit, kind="markets", items=items, sort=sort, status=status)

    @spun("Searching all events…")
    def fetchEvents(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = "volume",
        status: StatusKey | None = None,
    ) -> SearchResults:
        items = search_exchanges(
            query,
            limit,
            lambda name: fetchEvents(query, limit, exchange=name, sort=sort, status=status),
            event_to_result,
            label="events",
            sort=sort,
            exchanges=self.exchanges,
            on_error=self.on_error,
        )
        items = sort_event_results(items, sort)
        return SearchResults(query=query, limit=limit, kind="events", items=items, sort=sort, status=status)

    @spun("Searching all series…")
    def fetchSeries(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = "title",
        status: StatusKey | None = None,
    ) -> SearchResults:
        items = search_exchanges(
            query,
            limit,
            lambda name: fetchSeries(query, limit, exchange=name, sort=sort, status=status),
            series_to_result,
            label="series",
            sort=sort,
            exchanges=self.exchanges,
            on_error=self.on_error,
        )
        items = sort_series_results(items, sort)
        return SearchResults(query=query, limit=limit, kind="series", items=items, sort=sort, status=status)

    @spun()
    def fetchMatchedMarkets(self, query: str, limit: int = 10, *, sort: SortKey | None = None) -> list[Any]:
        kwargs: dict = {"query": query, "limit": limit}
        if sort:
            kwargs["sort"] = sort
        return pmxt.Router().fetch_matched_markets(**kwargs)

    @spun()
    def fetchMatchedPrices(self, query: str, limit: int = 10, *, sort: SortKey | None = None) -> list[Any]:
        kwargs: dict = {"query": query, "limit": limit}
        if sort:
            kwargs["sort"] = sort
        return pmxt.Router().fetch_matched_prices(**kwargs)

    @spun()
    def fetchArbitrage(self, query: str, limit: int = 10) -> list[Any]:
        return pmxt.Router().fetch_arbitrage(query=query, limit=limit)
