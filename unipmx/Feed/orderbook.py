"""Public Feed API — WebSocket order books."""

from typing import Any

from pmxt.models import OrderBook

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def watchOrderBook(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> OrderBook:
    return getClient(exchange).watch_order_book(outcome_id)


@spun()
def watchOrderBooks(
    outcome_ids: list[str],
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> dict[str, OrderBook]:
    return getClient(exchange).watch_order_books(outcome_ids)


@spun()
def watchAllOrderBooks(
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> Any:
    return getClient(exchange).watch_all_order_books()


@spun()
def unwatchOrderBook(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> None:
    getClient(exchange).unwatch_order_book(outcome_id)
