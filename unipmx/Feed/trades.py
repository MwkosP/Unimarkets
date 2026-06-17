"""Public Feed API — WebSocket trades."""

from pmxt.models import Trade

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE


@spun()
def watchTrades(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[Trade]:
    return getClient(exchange).watch_trades(outcome_id)


@spun()
def firehose(
    *,
    exchange: str = DEFAULT_EXCHANGE,
):
    return getClient(exchange).firehose()
