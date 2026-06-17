"""Public Events API — markets (REST)."""

from typing import Any

from pmxt.models import PaginatedMarketsResult, UnifiedMarket

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, DEFAULT_LIMIT, SortKey, StatusKey

from .utils import fetch_kwargs, sort_markets


@spun()
def fetchMarkets(
    event_id: str | None = None,
    query: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = None,
    status: StatusKey | None = None,
    **kwargs: Any,
) -> list[UnifiedMarket]:
    params = fetch_kwargs(query or "", limit, sort, status=status)
    if not query:
        params.pop("query", None)
    if event_id:
        params["event_id"] = event_id
    params.update(kwargs)
    markets = getClient(exchange).fetch_markets(**params)
    return sort_markets(markets, sort)


@spun()
def fetchMarket(
    market_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UnifiedMarket:
    return getClient(exchange).fetch_market(market_id=market_id)


@spun()
def fetchMarketsPaginated(
    query: str,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = None,
    status: StatusKey | None = None,
) -> PaginatedMarketsResult:
    result = getClient(exchange).fetch_markets_paginated(**fetch_kwargs(query, limit, sort, status=status))
    if sort and result.data:
        result.data[:] = sort_markets(list(result.data), sort)
    return result


@spun()
def loadMarkets(
    *,
    exchange: str = DEFAULT_EXCHANGE,
    reload: bool = False,
    sort: SortKey | None = None,
) -> dict[str, UnifiedMarket]:
    markets = getClient(exchange).load_markets(reload=reload)
    if sort:
        ordered = sort_markets(list(markets.values()), sort)
        return {m.market_id: m for m in ordered}
    return markets

