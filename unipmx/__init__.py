"""
unipmx — Polymarket / prediction market toolkit.

Architecture: Events/ Historical/ Users/ Feed/ Display/ Plots/
"""

from unipmx.Display import display
from unipmx.Plots import plotChart
from unipmx.clients import All, Kalshi, Limitless, Myriad, Polymarket, Probable, Smarkets
from unipmx.Events import (
    fetchEvent,
    fetchEvents,
    fetchMarket,
    fetchMarkets,
    fetchOrderBook,
    fetchOrderBookByQuery,
)
from unipmx.Feed import watchAddress, watchOrderBook, watchTrades
from unipmx.Historical import fetchOhlcv, fetchTrades
from unipmx.Users import UserActivity, fetchUserActivity, fetchUserBalance, fetchUserPositions, fetchUserTrades
from unipmx.client import getClient

__all__ = [
    "All",
    "Kalshi",
    "Limitless",
    "Myriad",
    "Polymarket",
    "Probable",
    "Smarkets",
    "UserActivity",
    "display",
    "plotChart",
    "fetchEvent",
    "fetchEvents",
    "fetchMarket",
    "fetchMarkets",
    "fetchOhlcv",
    "fetchOrderBook",
    "fetchOrderBookByQuery",
    "fetchTrades",
    "fetchUserActivity",
    "fetchUserBalance",
    "fetchUserPositions",
    "fetchUserTrades",
    "getClient",
    "watchAddress",
    "watchOrderBook",
    "watchTrades",
]
