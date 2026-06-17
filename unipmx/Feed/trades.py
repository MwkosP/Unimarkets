"""Public Feed API — WebSocket trades."""

from typing import Any

from pmxt.models import Trade

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import FeedError

from .helpers import safe_feed
from .polymarket import watch_polymarket_trades


@spun()
def watchTrades(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    address: str | None = None,
    since: int | None = None,
    limit: int | None = None,
    timeout: float = 30,
) -> list[Trade] | FeedError:
    if exchange == "Polymarket" and address is None and since is None:
        return watch_polymarket_trades(outcome_id, limit=limit, timeout=timeout)

    return safe_feed(
        "watchTrades",
        exchange,
        lambda: getClient(exchange).watch_trades(
            outcome_id,
            address=address,
            since=since,
            limit=limit,
        ),
    )


@spun()
def firehose(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    venues: list[str] | None = None,
) -> Any | FeedError:
    return safe_feed("firehose", exchange, lambda: getClient(exchange).firehose(venues=venues))
