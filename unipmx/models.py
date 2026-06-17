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
class HistoricalValuePoint:
    timestamp: int | None
    value: float | None
    kind: str
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class PlatformStats:
    venue: str
    markets_sampled: int
    active_markets: int
    closed_markets: int
    events_sampled: int
    volume: float | None
    liquidity: float | None
    open_interest: float | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class PlatformFee:
    venue: str
    market_id: str | None
    title: str | None
    fee: str | None
    maker_base_fee: float | None = None
    taker_base_fee: float | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class PlatformCategory:
    id: str | None
    label: str
    slug: str | None = None
    count: int | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class PlatformStatus:
    venue: str
    ok: bool
    components: dict[str, bool]
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class PlatformVenue:
    name: str
    supported: bool = True
    user_tracking: bool = False
    source: str = "unipmx"
    raw: dict | None = None


@dataclass
class FeedError:
    function: str
    message: str
    exchange: str
    hint: str | None = None
    source: str = "pmxt"
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


@dataclass
class UserProfile:
    address: str
    name: str | None = None
    pseudonym: str | None = None
    bio: str | None = None
    profile_image: str | None = None
    x_username: str | None = None
    verified: bool | None = None
    joined_at: str | None = None
    views: int | None = None
    positions_value: float | None = None
    biggest_win: float | None = None
    predictions: int | None = None
    profit_loss: float | None = None
    profit_loss_percent: float | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserWalletAge:
    user_address: str
    joined_at: str | None
    days: int | None
    years: float | None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserWalletConnection:
    user_address: str
    connection_id: str | None
    creator: bool | None = None
    mod: bool | None = None
    community_mod: bool | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserPosition:
    user_address: str
    market_id: str | None
    title: str | None
    outcome: str | None
    size: float
    avg_price: float | None
    current_price: float | None
    current_value: float | None
    cash_pnl: float | None
    percent_pnl: float | None
    realized_pnl: float | None
    status: str | None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserTradeRecord:
    user_address: str
    market_id: str | None
    title: str | None
    outcome: str | None
    side: str | None
    price: float | None
    size: float | None
    timestamp: int | None
    transaction_hash: str | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserActivityItem:
    user_address: str
    activity_type: str | None
    market_id: str | None
    title: str | None
    outcome: str | None
    side: str | None
    price: float | None
    size: float | None
    timestamp: int | None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserPnL:
    user_address: str
    window: str
    realized: float | None
    unrealized: float | None
    total: float | None
    percent: float | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserRank:
    user_address: str
    rank: int | None
    window: str
    by: str
    value: float | None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserStyle:
    user_address: str
    trader_type: str
    activity_style: str
    sizing_style: str
    directional_style: str
    flow_style: str
    recent_trades: int
    open_markets: int
    open_position_value: float
    average_position_value: float
    biggest_position_value: float
    profitable_positions: int
    losing_positions: int
    total_pnl: float | None
    pnl_percent: float | None
    rank: int | None
    preferred_keywords: list[str]
    data_available: bool = True
    errors: list[str] | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserLeaderboardEntry:
    rank: int | None
    user_address: str | None
    username: str | None
    volume: float | None
    pnl: float | None
    profile_image: str | None = None
    x_username: str | None = None
    verified: bool | None = None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserMarket:
    user_address: str
    market_id: str | None
    title: str | None
    outcomes: list[str]
    size: float
    current_value: float | None
    cash_pnl: float | None
    status: str | None
    source: str = "Polymarket"
    raw: dict | None = None


@dataclass
class UserPortfolioValue:
    user_address: str
    value: float | None
    source: str = "Polymarket"
    raw: dict | None = None
