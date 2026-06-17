"""Venue capability matrix — raises NotSupported when a method is unavailable."""

from unipmx.exceptions import NotSupported

SERIES_VENUES = frozenset({"Polymarket", "Kalshi"})

# Venues with a dedicated holders API wired in market_detail
HOLDERS_VENUES = frozenset({"Polymarket", "Limitless"})

# Venues with aggregate market positions API
POSITIONS_VENUES = frozenset({"Polymarket", "Limitless"})

# Venues with event comment threads
COMMENTS_VENUES = frozenset({"Polymarket"})


def ensure_supported(exchange: str, method: str) -> None:
    if method in ("fetchSeries", "fetchSeriesMarkets", "fetchSeriesEvents"):
        if exchange not in SERIES_VENUES:
            raise NotSupported(f"{method} is not supported on {exchange}")
