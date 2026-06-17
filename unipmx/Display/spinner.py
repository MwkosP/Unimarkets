"""Re-entrant dot spinner + decorator for all public fetch/watch APIs."""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import TypeVar

from .utils import loading

F = TypeVar("F", bound=Callable)

_LABELS: dict[str, str] = {
    "fetchMarkets": "Fetching markets…",
    "fetchMarket": "Fetching market…",
    "fetchMarketsPaginated": "Fetching markets (paginated)…",
    "loadMarkets": "Loading markets…",
    "searchAllMarkets": "Searching all markets…",
    "searchAll": "Searching all markets…",
    "fetchEvents": "Fetching events…",
    "fetchEvent": "Fetching event…",
    "searchAllEvents": "Searching all events…",
    "fetchSeries": "Fetching series…",
    "searchAllSeries": "Searching all series…",
    "fetchOrderBook": "Fetching order book…",
    "fetchOrderBooks": "Fetching order books…",
    "getOutcomeId": "Resolving outcome…",
    "fetchOrderBookByQuery": "Finding order book…",
    "filterMarkets": "Filtering markets…",
    "filterEvents": "Filtering events…",
    "compareExchanges": "Comparing exchanges…",
    "fetchMatchedMarkets": "Fetching matched markets…",
    "fetchMatchedPrices": "Fetching matched prices…",
    "fetchArbitrage": "Fetching arbitrage…",
    "fetchOhlcv": "Fetching OHLCV…",
    "fetchOhlcvByQuery": "Fetching OHLCV…",
    "fetchTrades": "Fetching trades…",
    "fetchUserTrades": "Fetching user trades…",
    "fetchUserPositions": "Fetching positions…",
    "fetchUserBalance": "Fetching balance…",
    "fetchUserActivity": "Fetching user activity…",
    "fetchOpenOrders": "Fetching open orders…",
    "fetchClosedOrders": "Fetching closed orders…",
    "fetchAllOrders": "Fetching orders…",
    "fetchOrder": "Fetching order…",
    "cancelOrder": "Cancelling order…",
    "watchOrderBook": "Watching order book…",
    "watchOrderBooks": "Watching order books…",
    "watchAllOrderBooks": "Watching all order books…",
    "watchTrades": "Watching trades…",
    "watchAddress": "Watching wallet…",
    "watchPrices": "Watching prices…",
    "watchUserPositions": "Watching user positions…",
    "watchUserTransactions": "Watching transactions…",
    "firehose": "Connecting firehose…",
    "unwatchOrderBook": "Stopping order book watch…",
    "unwatchAddress": "Stopping wallet watch…",
}


def spun(message: str | None = None) -> Callable[[F], F]:
    """Wrap a public API so it shows the dot spinner by default."""

    def decorator(fn: F) -> F:
        label = message or _LABELS.get(fn.__name__, f"{fn.__name__}…")

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            with loading(label):
                return fn(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
