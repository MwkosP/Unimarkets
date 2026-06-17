"""Shared data types."""

from dataclasses import dataclass
from typing import Any, Literal, Optional

from pmxt.models import PriceCandle, UnifiedEvent, UnifiedSeries

SearchKind = Literal["markets", "events", "series"]

_OHLCV_COLUMN_GETTERS = {
    "open": lambda c: c.open,
    "high": lambda c: c.high,
    "low": lambda c: c.low,
    "close": lambda c: c.close,
    "volume": lambda c: c.volume or 0.0,
    "time": lambda c: float(c.timestamp) if c.timestamp else 0.0,
}


@dataclass
class OhlcvSeries:
    """One OHLCV column — pass to display() for a line/volume chart."""

    name: str
    values: list[float]
    timestamps: list[int | None]


@dataclass
class OhlcvCandles:
    """OHLC candle bundle — pass to plot(frame['ohlc']) for a candlestick chart."""

    candles: list[PriceCandle]

    def __len__(self) -> int:
        return len(self.candles)

    def __iter__(self):
        return iter(self.candles)


_OHLC_KEYS = frozenset({"ohlc", "candles", "ohlcv", "candle", "candlestick"})


@dataclass
class OhlcvFrame:
    """OHLCV table with column access: frame['close'], frame['ohlc'], etc."""

    candles: list[PriceCandle]

    def __iter__(self):
        return iter(self.candles)

    def __len__(self) -> int:
        return len(self.candles)

    def __getitem__(self, key: str | int) -> PriceCandle | OhlcvSeries | OhlcvCandles:
        if isinstance(key, int):
            return self.candles[key]
        col = key.lower().strip()
        if col in _OHLC_KEYS:
            return OhlcvCandles(candles=self.candles)
        getter = _OHLCV_COLUMN_GETTERS.get(col)
        if not getter:
            raise KeyError(
                f"Unknown column {key!r} — use ohlc, open, high, low, close, volume, time"
            )
        return OhlcvSeries(
            name=col,
            values=[getter(c) for c in self.candles],
            timestamps=[c.timestamp for c in self.candles],
        )


@dataclass
class MarketResult:
    exchange: str
    title: str
    yes_price: Optional[float]
    no_price: Optional[float]
    volume: Optional[float]
    market_id: Optional[str] = None
    url: Optional[str] = None


@dataclass
class EventResult:
    exchange: str
    title: str
    market_count: int
    volume: Optional[float]
    event_id: str
    url: Optional[str] = None


@dataclass
class SeriesResult:
    exchange: str
    title: str
    series_id: str
    recurrence: Optional[str] = None
    url: Optional[str] = None


@dataclass
class SearchResults:
    """Cross-exchange search — query is stored here so display() needs it once."""

    query: str
    limit: int
    kind: SearchKind
    items: list[Any]
    sort: str | None = None
    status: str | None = None


class EventList(list[UnifiedEvent]):
    """Events from fetchEvents — still indexable; carries display options."""

    show_markets: bool

    def __init__(self, events: list[UnifiedEvent], *, show_markets: bool = True) -> None:
        super().__init__(events)
        self.show_markets = show_markets


class SeriesList(list[UnifiedSeries]):
    """Series from fetchSeries — still indexable; carries display options."""

    show_events: bool
    show_markets: bool

    def __init__(
        self,
        series: list[UnifiedSeries],
        *,
        show_events: bool = True,
        show_markets: bool = True,
    ) -> None:
        super().__init__(series)
        self.show_events = show_events
        self.show_markets = show_markets


@dataclass
class Comment:
    id: str
    body: str
    author: str | None
    created_at: str | None
    source: str
    raw: dict
    parent_comment_id: str | None = None
    reply_to: str | None = None
    reaction_count: int = 0


@dataclass
class Holder:
    address: str
    amount: float
    outcome: str | None
    name: str | None
    source: str
    raw: dict


@dataclass
class MarketStats:
    market_id: str
    volume: float | None
    liquidity: float | None
    open_interest: float | None
    unique_traders: int | None
    source: str
    raw: dict


@dataclass
class Resolution:
    market_id: str
    status: str | None
    outcome: str | None
    resolved_by: str | None
    resolved_at: str | None
    resolution_source: str | None
    source: str
    raw: dict


@dataclass
class MarketRules:
    market_id: str
    description: str | None
    resolution_source: str | None
    criteria: str | None
    source: str
    raw: dict


@dataclass
class PricePoint:
    timestamp: int
    yes_price: float | None
    no_price: float | None
    source: str
    raw: dict | None = None


@dataclass
class MarketPosition:
    address: str
    outcome: str | None
    size: float
    avg_price: float | None
    current_value: float | None
    source: str
    raw: dict
