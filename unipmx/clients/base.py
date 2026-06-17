"""Venue client base — all Events methods bound to one exchange."""

from __future__ import annotations

from typing import Any, Callable

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
from unipmx.Feed import (
    firehose,
    unwatchAddress,
    unwatchOrderBook,
    watchAddress,
    watchAllOrderBooks,
    watchOrderBook,
    watchOrderBooks,
    watchPrices,
    watchTrades,
    watchUserPositions,
    watchUserTransactions,
)
from unipmx.Historical import (
    fetchHistorical,
    fetchHistoricalEventPrice,
    fetchHistoricalMarketOpenInterest,
    fetchHistoricalMarketPrice,
    fetchHistoricalMarketPriceOhlcv,
    fetchHistoricalMarketTrades,
    fetchHistoricalMarketVolume,
    fetchHistoricalUserPnl,
    fetchHistoricalUserTradeHistory,
    fetchHistoricalUserWalletConnections,
)
from unipmx.Platform import (
    fetchPlatformCategories,
    fetchPlatformFees,
    fetchPlatformStats,
    fetchPlatformStatus,
    fetchPlatformVenues,
)
from unipmx.Users import (
    fetchUserActivity,
    fetchUserFollowers,
    fetchUserFollowing,
    fetchUserMarkets,
    fetchUserPnL,
    fetchUserPortfolioValue,
    fetchUserPositions,
    fetchUserProfile,
    fetchUserRank,
    fetchUserTrades,
    fetchUserWalletAge,
    fetchUserWalletConnections,
    fetchUsersLeaderboard,
    findUserStyle,
)


class ExchangeClient:
    """Base client — subclass sets ``exchange`` (e.g. ``Polymarket``)."""

    exchange: str

    def __init__(
        self,
        *,
        wallet_address: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self._wallet_address = wallet_address
        self._api_key = api_key
        self._client = None

    @property
    def name(self) -> str:
        return self.exchange

    @property
    def client(self):
        if self._client is None:
            self._client = getClient(
                self.exchange,
                wallet_address=self._wallet_address,
                api_key=self._api_key,
            )
        return self._client

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

    # ── Users ─────────────────────────────────────────────────────────────

    def fetchUserProfile(self, user_address: str):
        return fetchUserProfile(user_address, exchange=self.exchange)

    def fetchUserWalletAge(self, user_address: str):
        return fetchUserWalletAge(user_address, exchange=self.exchange)

    def fetchUserWalletConnections(self, user_address: str, limit: int = 20):
        return fetchUserWalletConnections(user_address, limit=limit, exchange=self.exchange)

    def fetchUserPositions(
        self,
        user_address: str,
        status: str = "open",
        sort: str | None = None,
        limit: int = 20,
    ):
        return fetchUserPositions(
            user_address,
            status=status,
            sort=sort,
            limit=limit,
            exchange=self.exchange,
        )

    def fetchUserTrades(
        self,
        user_address: str,
        market_id: str | None = None,
        sort: str | None = None,
        limit: int = 20,
    ):
        return fetchUserTrades(
            user_address,
            market_id=market_id,
            sort=sort,
            limit=limit,
            exchange=self.exchange,
        )

    def fetchUserActivity(
        self,
        user_address: str,
        type: str | None = None,
        market_id: str | None = None,
        limit: int = 20,
    ):
        return fetchUserActivity(
            user_address,
            type=type,
            market_id=market_id,
            limit=limit,
            exchange=self.exchange,
        )

    def fetchUserPnL(self, user_address: str, window: str = "all"):
        return fetchUserPnL(user_address, window=window, exchange=self.exchange)

    def fetchUserRank(
        self,
        user_address: str,
        window: str = "all",
        by: str = "profit",
    ):
        return fetchUserRank(user_address, window=window, by=by, exchange=self.exchange)

    def fetchUsersLeaderboard(
        self,
        limit: int = 20,
        window: str = "all",
        by: str = "profit",
    ):
        return fetchUsersLeaderboard(limit=limit, window=window, by=by, exchange=self.exchange)

    def fetchUserMarkets(
        self,
        user_address: str,
        status: str | None = None,
        limit: int = 20,
    ):
        return fetchUserMarkets(user_address, status=status, limit=limit, exchange=self.exchange)

    def fetchUserPortfolioValue(self, user_address: str):
        return fetchUserPortfolioValue(user_address, exchange=self.exchange)

    def fetchUserFollowers(self, user_address: str, limit: int = 20):
        return fetchUserFollowers(user_address, limit=limit, exchange=self.exchange)

    def fetchUserFollowing(self, user_address: str, limit: int = 20):
        return fetchUserFollowing(user_address, limit=limit, exchange=self.exchange)

    def findUserStyle(self, user_address: str, **kwargs: Any):
        return findUserStyle(user_address, exchange=self.exchange, **kwargs)

    # ── Historical ────────────────────────────────────────────────────────

    def fetchHistoricalMarketPrice(self, market_id: str, **kwargs: Any):
        return fetchHistoricalMarketPrice(market_id, exchange=self.exchange, **kwargs)

    def fetchHistoricalMarketPriceOhlcv(self, market_id: str, **kwargs: Any):
        return fetchHistoricalMarketPriceOhlcv(market_id, exchange=self.exchange, **kwargs)

    def fetchHistoricalMarketVolume(self, market_id: str, **kwargs: Any):
        return fetchHistoricalMarketVolume(market_id, exchange=self.exchange, **kwargs)

    def fetchHistoricalMarketTrades(self, market_id: str, **kwargs: Any):
        return fetchHistoricalMarketTrades(market_id, exchange=self.exchange, **kwargs)

    def fetchHistoricalMarketOpenInterest(self, market_id: str, **kwargs: Any):
        return fetchHistoricalMarketOpenInterest(market_id, exchange=self.exchange, **kwargs)

    def fetchHistoricalEventPrice(self, event_id: str, **kwargs: Any):
        return fetchHistoricalEventPrice(event_id, exchange=self.exchange, **kwargs)

    def fetchHistorical(self, id: str, **kwargs: Any):
        return fetchHistorical(id, exchange=self.exchange, **kwargs)

    def fetchHistoricalUserTradeHistory(self, user_address: str, **kwargs: Any):
        return fetchHistoricalUserTradeHistory(user_address, exchange=self.exchange, **kwargs)

    def fetchHistoricalUserPnl(self, user_address: str, **kwargs: Any):
        return fetchHistoricalUserPnl(user_address, exchange=self.exchange, **kwargs)

    def fetchHistoricalUserWalletConnections(self, user_address: str, **kwargs: Any):
        return fetchHistoricalUserWalletConnections(user_address, exchange=self.exchange, **kwargs)

    # ── Feed ──────────────────────────────────────────────────────────────

    def watchTrades(
        self,
        outcome_id: str,
        *,
        address: str | None = None,
        since: int | None = None,
        limit: int | None = None,
        timeout: float = 30,
    ):
        return watchTrades(
            outcome_id,
            exchange=self.exchange,
            address=address,
            since=since,
            limit=limit,
            timeout=timeout,
        )

    def firehose(self, *, venues: list[str] | None = None):
        return firehose(exchange=self.exchange, venues=venues)

    def watchOrderBook(
        self,
        outcome_id: str,
        *,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ):
        return watchOrderBook(outcome_id, exchange=self.exchange, limit=limit, params=params)

    def watchOrderBooks(
        self,
        outcome_ids: list[str],
        *,
        limit: int | None = None,
        params: dict[str, Any] | None = None,
    ):
        return watchOrderBooks(outcome_ids, exchange=self.exchange, limit=limit, params=params)

    def watchAllOrderBooks(self, *, venues: list[str] | None = None):
        return watchAllOrderBooks(exchange=self.exchange, venues=venues)

    def unwatchOrderBook(self, outcome_id: str):
        return unwatchOrderBook(outcome_id, exchange=self.exchange)

    def watchAddress(self, address: str, *, types: list[str] | None = None):
        return watchAddress(address, exchange=self.exchange, types=types)

    def unwatchAddress(self, address: str):
        return unwatchAddress(address, exchange=self.exchange)

    def watchUserPositions(
        self,
        *,
        wallet_address: str | None = None,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        return watchUserPositions(
            exchange=self.exchange,
            wallet_address=wallet_address or self._wallet_address,
            callback=callback,
        )

    def watchUserTransactions(
        self,
        *,
        wallet_address: str | None = None,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        return watchUserTransactions(
            exchange=self.exchange,
            wallet_address=wallet_address or self._wallet_address,
            callback=callback,
        )

    def watchPrices(
        self,
        market_address: str,
        *,
        callback: Callable[[dict[str, Any]], None] | None = None,
    ):
        return watchPrices(market_address, exchange=self.exchange, callback=callback)

    # ── Platform ──────────────────────────────────────────────────────────

    def fetchPlatformStats(self, **kwargs: Any):
        return fetchPlatformStats(exchange=self.exchange, **kwargs)

    def fetchPlatformFees(self, **kwargs: Any):
        return fetchPlatformFees(exchange=self.exchange, **kwargs)

    def fetchPlatformCategories(self, **kwargs: Any):
        return fetchPlatformCategories(exchange=self.exchange, **kwargs)

    def fetchPlatformStatus(self, **kwargs: Any):
        return fetchPlatformStatus(exchange=self.exchange, **kwargs)

    def fetchPlatformVenues(self, **kwargs: Any):
        return fetchPlatformVenues(exchange=self.exchange, **kwargs)
