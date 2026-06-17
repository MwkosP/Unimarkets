"""Public Feed API — WebSocket order books."""

from typing import Any

from pmxt.models import OrderBook

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import FeedError

from .helpers import safe_feed


@spun()
def watchOrderBook(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
) -> OrderBook | FeedError:
    return safe_feed(
        "watchOrderBook",
        exchange,
        lambda: getClient(exchange).watch_order_book(outcome_id, limit=limit, params=params),
    )


@spun()
def watchOrderBooks(
    outcome_ids: list[str],
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, OrderBook] | FeedError:
    return safe_feed(
        "watchOrderBooks",
        exchange,
        lambda: getClient(exchange).watch_order_books(outcome_ids, limit=limit, params=params),
    )


@spun()
def watchAllOrderBooks(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    venues: list[str] | None = None,
) -> Any | FeedError:
    return safe_feed(
        "watchAllOrderBooks",
        exchange,
        lambda: getClient(exchange).watch_all_order_books(venues=venues),
    )


@spun()
def unwatchOrderBook(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> None | FeedError:
    return safe_feed(
        "unwatchOrderBook",
        exchange,
        lambda: getClient(exchange).unwatch_order_book(outcome_id),
    )
