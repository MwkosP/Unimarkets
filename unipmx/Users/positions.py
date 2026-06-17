"""Public Users API — open positions."""

from pmxt.models import Position

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def fetchUserPositions(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[Position]:
    return getClient(exchange, wallet_address=address).fetch_positions(address)
