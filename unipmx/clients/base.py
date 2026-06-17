"""Venue client base — all Events methods bound to one exchange."""

from __future__ import annotations

from typing import Any

from unipmx.client import getClient
from unipmx.config import DEFAULT_LIMIT, ResolutionKey, SortKey, StatusKey
from unipmx.Events.events import fetchEvent, fetchEventComments, fetchEvents, fetchRelatedEvents
from unipmx.Events.filter import filterEvents, filterMarkets
from unipmx.Events.market_detail import (
    fetchMarketActivity,
    fetchMarketGraph,
    fetchMarketOrderBook,
    fetchMarketPositions,
    fetchMarketResolution,
    fetchMarketRules,
    fetchMarketStats,
    fetchMarketTopHolders,
)
from unipmx.Events.markets import fetchMarket, fetchMarkets, fetchMarketsPaginated, loadMarkets
from unipmx.Events.orderbook import fetchOrderBook, fetchOrderBookByQuery, fetchOrderBooks, getOutcomeId
from unipmx.Events.series import fetchSeries, fetchSeriesEvents, fetchSeriesMarkets


class ExchangeClient:
    """Base client — subclass sets ``exchange`` (e.g. ``Polymarket``)."""

    exchange: str

    def __init__(
        self,
        *,
        wallet_address: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._client = getClient(
            self.exchange,
            wallet_address=wallet_address,
            api_key=api_key,
        )

    @property
    def name(self) -> str:
        return self.exchange

    # ── Events ────────────────────────────────────────────────────────────

    def fetchEvents(
        self,
        query: str | None = None,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = None,
        status: StatusKey | None = None,
        show_markets: bool = True,
        **kwargs: Any,
    ):
        return fetchEvents(
            query,
            limit,
            exchange=self.exchange,
            sort=sort,
            status=status,
            show_markets=show_markets,
            **kwargs,
        )

    def fetchEvent(self, event_id: str, **kwargs: Any):
        return fetchEvent(event_id, exchange=self.exchange, **kwargs)

    def fetchEventComments(self, event_id: str, limit: int = DEFAULT_LIMIT, **kwargs: Any):
        return fetchEventComments(event_id, limit, exchange=self.exchange, **kwargs)

    def fetchRelatedEvents(
        self,
        event_id: str,
        *,
        limit: int = DEFAULT_LIMIT,
        show_markets: bool = True,
        **kwargs: Any,
    ):
        return fetchRelatedEvents(
            event_id, limit=limit, exchange=self.exchange, show_markets=show_markets, **kwargs
        )

    # ── Markets ───────────────────────────────────────────────────────────

    def fetchMarkets(
        self,
        query: str | None = None,
        *,
        event_id: str | None = None,
        limit: int = DEFAULT_LIMIT,
        sort: SortKey | None = None,
        status: StatusKey | None = None,
        **kwargs: Any,
    ):
        return fetchMarkets(
            event_id,
            query,
            limit,
            exchange=self.exchange,
            sort=sort,
            status=status,
            **kwargs,
        )

    def fetchMarket(self, market_id: str, **kwargs: Any):
        return fetchMarket(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketsPaginated(
        self,
        query: str,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = None,
        status: StatusKey | None = None,
        **kwargs: Any,
    ):
        return fetchMarketsPaginated(
            query, limit, exchange=self.exchange, sort=sort, status=status, **kwargs
        )

    def loadMarkets(self, *, reload: bool = False, sort: SortKey | None = None):
        return loadMarkets(exchange=self.exchange, reload=reload, sort=sort)

    # ── Market detail ─────────────────────────────────────────────────────

    def fetchMarketOrderBook(self, market_id: str, **kwargs: Any):
        return fetchMarketOrderBook(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketActivity(self, market_id: str, limit: int = DEFAULT_LIMIT, **kwargs: Any):
        return fetchMarketActivity(market_id, limit, exchange=self.exchange, **kwargs)

    def fetchMarketTopHolders(self, market_id: str, **kwargs: Any):
        return fetchMarketTopHolders(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketStats(self, market_id: str, **kwargs: Any):
        return fetchMarketStats(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketResolution(self, market_id: str, **kwargs: Any):
        return fetchMarketResolution(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketRules(self, market_id: str, **kwargs: Any):
        return fetchMarketRules(market_id, exchange=self.exchange, **kwargs)

    def fetchMarketGraph(
        self,
        market_id: str,
        *,
        resolution: ResolutionKey = "1d",
        limit: int | None = None,
        **kwargs: Any,
    ):
        return fetchMarketGraph(
            market_id,
            exchange=self.exchange,
            resolution=resolution,
            limit=limit,
            **kwargs,
        )

    def fetchMarketPositions(
        self,
        market_id: str,
        *,
        limit: int | None = None,
        **kwargs: Any,
    ):
        return fetchMarketPositions(
            market_id, exchange=self.exchange, limit=limit, **kwargs
        )

    # ── Order books ───────────────────────────────────────────────────────

    def fetchOrderBook(self, outcome_id: str, *, limit: float | None = None):
        return fetchOrderBook(outcome_id, exchange=self.exchange, limit=limit)

    def fetchOrderBooks(self, outcome_ids: list[str]):
        return fetchOrderBooks(outcome_ids, exchange=self.exchange)

    def getOutcomeId(
        self,
        query: str,
        *,
        market_index: int = 0,
        outcome_index: int | None = None,
        active_only: bool = True,
    ):
        return getOutcomeId(
            query,
            exchange=self.exchange,
            market_index=market_index,
            outcome_index=outcome_index,
            active_only=active_only,
        )

    def fetchOrderBookByQuery(
        self,
        query: str,
        *,
        outcome_index: int | None = None,
        active_only: bool = True,
    ):
        return fetchOrderBookByQuery(
            query,
            exchange=self.exchange,
            outcome_index=outcome_index,
            active_only=active_only,
        )

    # ── Series ────────────────────────────────────────────────────────────

    def fetchSeries(
        self,
        query: str | None = None,
        limit: int = DEFAULT_LIMIT,
        *,
        sort: SortKey | None = "title",
        status: StatusKey | None = None,
        show_events: bool = True,
        show_markets: bool = True,
        **kwargs: Any,
    ):
        return fetchSeries(
            query,
            limit,
            exchange=self.exchange,
            sort=sort,
            status=status,
            show_events=show_events,
            show_markets=show_markets,
            **kwargs,
        )

    def fetchSeriesMarkets(
        self,
        series_id: str,
        status: StatusKey | None = None,
        sort: SortKey | None = None,
        limit: int = DEFAULT_LIMIT,
        **kwargs: Any,
    ):
        return fetchSeriesMarkets(
            series_id,
            status,
            sort,
            limit,
            exchange=self.exchange,
            **kwargs,
        )

    def fetchSeriesEvents(
        self,
        series_id: str,
        status: StatusKey | None = None,
        sort: SortKey | None = None,
        limit: int = DEFAULT_LIMIT,
        **kwargs: Any,
    ):
        return fetchSeriesEvents(
            series_id,
            status,
            sort,
            limit,
            exchange=self.exchange,
            **kwargs,
        )

    # ── Filter ────────────────────────────────────────────────────────────

    def filterMarkets(
        self,
        markets,
        criteria: str | dict | Any,
        *,
        sort: SortKey | None = None,
    ):
        return filterMarkets(markets, criteria, exchange=self.exchange, sort=sort)

    def filterEvents(
        self,
        events,
        criteria: str | dict | Any,
        *,
        sort: SortKey | None = None,
    ):
        return filterEvents(events, criteria, exchange=self.exchange, sort=sort)
