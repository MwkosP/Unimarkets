"""Venue clients — instantiate explicitly, never via exchange string."""

from unipmx.clients.all import All
from unipmx.clients.base import ExchangeClient


class Polymarket(ExchangeClient):
    exchange = "Polymarket"


class Kalshi(ExchangeClient):
    exchange = "Kalshi"


class Limitless(ExchangeClient):
    exchange = "Limitless"


class Myriad(ExchangeClient):
    exchange = "Myriad"


class Probable(ExchangeClient):
    exchange = "Probable"


class Smarkets(ExchangeClient):
    exchange = "Smarkets"


__all__ = [
    "All",
    "ExchangeClient",
    "Kalshi",
    "Limitless",
    "Myriad",
    "Polymarket",
    "Probable",
    "Smarkets",
]
