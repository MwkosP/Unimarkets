"""Public Users API — orders."""

from pmxt.models import Order

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def fetchOpenOrders(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
    market_id: str | None = None,
) -> list[Order]:
    client = getClient(exchange, wallet_address=wallet_address)
    return client.fetch_open_orders(market_id)


@spun()
def fetchClosedOrders(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> list[Order]:
    client = getClient(exchange, wallet_address=wallet_address)
    return client.fetch_closed_orders()


@spun()
def fetchAllOrders(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> list[Order]:
    client = getClient(exchange, wallet_address=wallet_address)
    return client.fetch_all_orders()


@spun()
def fetchOrder(
    order_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> Order:
    client = getClient(exchange, wallet_address=wallet_address)
    return client.fetch_order(order_id)


@spun()
def cancelOrder(
    order_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    wallet_address: str | None = None,
) -> Order:
    client = getClient(exchange, wallet_address=wallet_address)
    return client.cancel_order(order_id)
