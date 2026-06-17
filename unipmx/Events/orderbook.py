"""Public Events API — order books (REST)."""

from pmxt.errors import NotFoundError
from pmxt.models import MarketOutcome, OrderBook, UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.Display.utils import loading
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, DEFAULT_LIMIT

from .markets import fetchMarkets


@spun()
def fetchOrderBook(
    outcome_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: float | None = None,
) -> OrderBook:
    return getClient(exchange).fetch_order_book(outcome_id, limit=limit)


@spun()
def fetchOrderBooks(
    outcome_ids: list[str],
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> dict[str, OrderBook]:
    return getClient(exchange).fetch_order_books(outcome_ids)


@spun()
def getOutcomeId(
    query: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    market_index: int = 0,
    outcome_index: int | None = None,
    active_only: bool = True,
) -> tuple[UnifiedMarket, MarketOutcome]:
    """
    Resolve outcome_id from a search query.

    Use active_only=True (default) to skip resolved outcomes (price 0% or 100%)
    that have no live order book.
    """
    markets = fetchMarkets(query, limit=max(market_index + 1, DEFAULT_LIMIT), exchange=exchange)
    if not markets:
        raise ValueError(f"No market found for query '{query}'")

    if outcome_index is not None:
        market = markets[market_index]
        return market, market.outcomes[outcome_index]

    candidates = markets[market_index:] if market_index else markets
    for market in candidates:
        for outcome in market.outcomes:
            if active_only and not (0.01 < outcome.price < 0.99):
                continue
            return market, outcome

    return markets[market_index], markets[market_index].outcomes[0]


def fetchOrderBookByQuery(
    query: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    outcome_index: int | None = None,
    active_only: bool = True,
) -> tuple[UnifiedMarket, MarketOutcome, OrderBook] | None:
    """Find first market/outcome with a live order book for query."""
    with loading(f"Finding order book for '{query}'…") as status:
        markets = fetchMarkets(query, limit=DEFAULT_LIMIT, exchange=exchange)
        if not markets:
            return None

        for market in markets:
            status.update(f"[dim]Checking[/dim] {market.title[:40]}…")
            outcomes = market.outcomes
            if outcome_index is not None:
                outcomes = [market.outcomes[outcome_index]]

            for outcome in outcomes:
                if active_only and not (0.01 < outcome.price < 0.99):
                    continue
                try:
                    book = fetchOrderBook(outcome.outcome_id, exchange=exchange)
                    return market, outcome, book
                except NotFoundError:
                    continue

    return None
