"""Public Feed API — user-specific streams (authenticated wallet)."""

from typing import Any

from pmxt.models import Position

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def watchUserPositions(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> list[Position]:
    return getClient(exchange, wallet_address=wallet_address).watch_user_positions()


@spun()
def watchUserTransactions(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> dict[str, Any]:
    return getClient(exchange, wallet_address=wallet_address).watch_user_transactions()


@spun()
def watchPrices(
    market_address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> dict[str, Any]:
    return getClient(exchange).watch_prices(market_address)
