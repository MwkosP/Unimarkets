"""Exchange registry and defaults."""

import os
from typing import Literal

_node_options = os.environ.get("NODE_OPTIONS", "")
if "--use-system-ca" not in _node_options:
    os.environ["NODE_OPTIONS"] = f"{_node_options} --use-system-ca".strip()

import pmxt

DEFAULT_EXCHANGE = "Polymarket"

EXCHANGES: dict[str, type] = {
    "Polymarket": pmxt.Polymarket,
    "Kalshi": pmxt.Kalshi,
    "Limitless": pmxt.Limitless,
    "Myriad": pmxt.Myriad,
    "Probable": pmxt.Probable,
    "Smarkets": pmxt.Smarkets,
}

DEFAULT_QUERY = "bitcoin"
DEFAULT_LIMIT = 5
DEFAULT_PLOT_LIMIT = 168  # ~1 week of 1h candles — fast default for plotChart
ARBITRAGE_THRESHOLD = 0.03

# volume | liquidity | newest → API + local re-sort
# title | market_count → local only
SortKey = Literal["volume", "liquidity", "newest", "title", "market_count"]
API_SORT_KEYS = frozenset({"volume", "liquidity", "newest"})

# OHLCV candle resolutions — use with fetchOhlcv / fetchOhlcvByQuery
ResolutionKey = Literal["1m", "5m", "15m", "1h", "4h", "1d", "max"]

# plotChart styles
ChartStyleKey = Literal["candles", "line"]

# active | inactive | closed | all — passed to pmxt fetch_markets / fetch_events
StatusKey = Literal["active", "inactive", "closed", "all"]
