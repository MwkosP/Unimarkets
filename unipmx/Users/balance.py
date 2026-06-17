"""Public Users API — wallet balances."""

from pmxt.models import Balance

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def fetchUserBalance(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[Balance]:
    return getClient(exchange, wallet_address=address).fetch_balance(address)
