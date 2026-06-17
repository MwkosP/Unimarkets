"""Unified display — one function for all unipmx data types."""

from __future__ import annotations

from typing import Any, Literal

from pmxt.models import (
    Balance,
    Order,
    OrderBook,
    Position,
    PriceCandle,
    SubscribedAddressSnapshot,
    Trade,
    UnifiedEvent,
    UnifiedMarket,
    UnifiedSeries,
    UserTrade,
)

from unipmx.models import (
    Comment,
    EventList,
    EventResult,
    Holder,
    MarketPosition,
    MarketResult,
    MarketRules,
    MarketStats,
    OhlcvCandles,
    OhlcvFrame,
    OhlcvSeries,
    PricePoint,
    Resolution,
    SearchResults,
    SeriesList,
    SeriesResult,
)
from unipmx.Plots import plotChart

from .utils import (
    render_address_snapshot,
    render_balances,
    render_comments,
    render_compare,
    render_events,
    render_generic,
    render_holders,
    render_market_positions,
    render_market_rules,
    render_market_stats,
    render_markets,
    render_ohlcv,
    render_order_book,
    render_order_books,
    render_orders,
    render_positions,
    render_price_points,
    render_resolution,
    render_search_events,
    render_search_results,
    render_search_series,
    render_series,
    render_trades,
    render_user_activity,
    show_panel,
)


def display(
    data: Any,
    *,
    title: str | None = None,
    exchange: str | None = None,
    query: str | None = None,
    limit: int | None = None,
    address: str | None = None,
    chart: Literal["browser", "terminal"] = "browser",
) -> None:
    """
    Render any unipmx data type to the terminal — exactly one bordered panel per call.

    OHLCV series/candles delegate to :mod:`unipmx.Plots` when ``chart="browser"``.
    """
    if isinstance(data, OhlcvCandles):
        if chart == "terminal":
            show_panel(render_ohlcv(data.candles, title=title or "OHLCV"))
        else:
            plotChart(data, title=title or "OHLC", style="candles")
        return

    if isinstance(data, OhlcvSeries):
        plotChart(data, title=title, terminal=(chart == "terminal"), style="line")
        return

    if isinstance(data, OhlcvFrame):
        show_panel(render_ohlcv(data.candles, title=title or "OHLCV"))
        return

    panel = _panel_for(
        data,
        title=title,
        exchange=exchange,
        query=query,
        limit=limit,
        address=address,
    )
    if panel is not None:
        show_panel(panel)


def _panel_for(
    data: Any,
    *,
    title: str | None,
    exchange: str | None,
    query: str | None,
    limit: int | None,
    address: str | None,
):
    if data is None:
        return render_generic(None, title=title or "Empty")

    if isinstance(data, SearchResults):
        if data.kind == "markets":
            return render_search_results(data.items, query=data.query, sort=data.sort, status=data.status)
        if data.kind == "events":
            return render_search_events(data.items, query=data.query, sort=data.sort, status=data.status)
        return render_search_series(data.items, query=data.query, sort=data.sort)

    if type(data).__name__ == "UserActivity":
        return render_user_activity(data, title=title or "User Activity")

    if isinstance(data, SubscribedAddressSnapshot):
        return render_address_snapshot(data, title=title or "Wallet Feed")

    if isinstance(data, UnifiedMarket):
        return render_markets(data, title=title or "Market", exchange=exchange, query=query, limit=limit)

    if isinstance(data, UnifiedEvent):
        return render_events(data, title=title or "Event", exchange=exchange, query=query)

    if isinstance(data, EventList):
        return render_events(
            data,
            title=title or "Events",
            exchange=exchange,
            query=query,
            show_markets=data.show_markets,
        )

    if isinstance(data, SeriesList):
        return render_series(
            data,
            title=title or "Series",
            exchange=exchange,
            query=query,
            show_events=data.show_events,
            show_markets=data.show_markets,
        )

    if isinstance(data, MarketStats):
        return render_market_stats(data, title=title or "Market Stats")

    if isinstance(data, Resolution):
        return render_resolution(data, title=title or "Resolution")

    if isinstance(data, MarketRules):
        return render_market_rules(data, title=title or "Market Rules")

    if isinstance(data, tuple) and len(data) == 3:
        return render_order_book(data, title=title or "Order Book", exchange=exchange, query=query)

    if isinstance(data, OrderBook):
        return render_order_book(data, title=title or "Order Book", exchange=exchange, query=query)

    if isinstance(data, dict):
        if data and all(isinstance(v, list) and (not v or isinstance(v[0], UnifiedMarket)) for v in data.values()):
            return render_compare(data, query=query or "")
        if data and all(isinstance(v, OrderBook) for v in data.values()):
            return render_order_books(data, title=title or "Order Books", exchange=exchange)
        return render_generic(data, title=title or "Data")

    if not isinstance(data, list):
        return render_generic(data, title=title or type(data).__name__)

    if not data:
        t = (title or "").lower()
        if "ohlcv" in t:
            return render_ohlcv(data, title=title or "OHLCV")
        if "trade" in t:
            return render_trades(data, title=title or "Trades")
        return render_generic([], title=title or "Empty")

    first = data[0]

    if isinstance(first, UnifiedMarket):
        return render_markets(data, title=title or "Markets", exchange=exchange, query=query, limit=limit)
    if isinstance(first, UnifiedEvent):
        show_markets = getattr(data, "show_markets", True)
        return render_events(
            data, title=title or "Events", exchange=exchange, query=query, show_markets=show_markets
        )
    if isinstance(first, UnifiedSeries):
        show_events = getattr(data, "show_events", True)
        show_markets = getattr(data, "show_markets", True)
        return render_series(
            data,
            title=title or "Series",
            exchange=exchange,
            query=query,
            show_events=show_events,
            show_markets=show_markets,
        )
    if isinstance(first, EventResult):
        return render_search_events(data, query=query or "")
    if isinstance(first, MarketResult):
        return render_search_results(data, query=query or "")
    if isinstance(first, SeriesResult):
        return render_search_series(data, query=query or "")
    if isinstance(first, (Trade, UserTrade)):
        return render_trades(data, title=title or "Trades")
    if isinstance(first, Position):
        return render_positions(data, title=title or "Positions", address=address)
    if isinstance(first, Balance):
        return render_balances(data, title=title or "Balance", address=address)
    if isinstance(first, Order):
        return render_orders(data, title=title or "Orders")
    if isinstance(first, PriceCandle):
        return render_ohlcv(data, title=title or "OHLCV")
    if isinstance(first, Comment):
        return render_comments(data, title=title or "Comments")
    if isinstance(first, Holder):
        return render_holders(data, title=title or "Top Holders")
    if isinstance(first, PricePoint):
        return render_price_points(data, title=title or "Price History")
    if isinstance(first, MarketPosition):
        return render_market_positions(data, title=title or "Market Positions")

    return render_generic(data, title=title or "Data")
