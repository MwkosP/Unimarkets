"""Public Events API — filter markets/events."""

from typing import Callable

from pmxt.models import UnifiedEvent, UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, SortKey

from .utils import sort_events, sort_markets


@spun()
def filterMarkets(
    markets: list[UnifiedMarket],
    criteria: str | dict | Callable,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = None,
) -> list[UnifiedMarket]:
    filtered = getClient(exchange).filter_markets(markets, criteria)
    return sort_markets(filtered, sort)


@spun()
def filterEvents(
    events: list[UnifiedEvent],
    criteria: str | dict | Callable,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = None,
) -> list[UnifiedEvent]:
    filtered = getClient(exchange).filter_events(events, criteria)
    return sort_events(filtered, sort)
