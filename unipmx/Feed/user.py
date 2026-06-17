"""Public Feed API — user-specific streams (authenticated wallet)."""

from typing import Any, Callable

from pmxt.models import Position

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import FeedError

from .helpers import safe_feed


@spun()
def watchUserPositions(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
    callback: Callable[[dict[str, Any]], None] | None = None,
) -> list[Position] | FeedError:
    return safe_feed(
        "watchUserPositions",
        exchange,
        lambda: getClient(exchange, wallet_address=wallet_address).watch_user_positions(
            callback=callback
        ),
    )


@spun()
def watchUserTransactions(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
    callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any] | FeedError:
    return safe_feed(
        "watchUserTransactions",
        exchange,
        lambda: getClient(exchange, wallet_address=wallet_address).watch_user_transactions(
            callback=callback
        ),
    )


@spun()
def watchPrices(
    market_address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    callback: Callable[[dict[str, Any]], None] | None = None,
) -> dict[str, Any] | FeedError:
    return safe_feed(
        "watchPrices",
        exchange,
        lambda: getClient(exchange).watch_prices(market_address, callback=callback),
    )
