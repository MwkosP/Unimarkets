"""Public Feed API — watch any public wallet."""

from pmxt.models import SubscribedAddressSnapshot

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def watchAddress(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    types: list[str] | None = None,
) -> SubscribedAddressSnapshot:
    return getClient(exchange).watch_address(address, types=types)


@spun()
def unwatchAddress(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> None:
    getClient(exchange).unwatch_address(address)
