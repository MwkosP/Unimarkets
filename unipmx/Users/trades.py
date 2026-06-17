"""Public Users API — wallet trade history."""

from pmxt.models import UserTrade

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def fetchUserTrades(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int | None = None,
) -> list[UserTrade]:
    client = getClient(exchange, wallet_address=address)
    kwargs = {"limit": limit} if limit else {}
    return client.fetch_my_trades(**kwargs)
