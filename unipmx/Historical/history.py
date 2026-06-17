"""Public Historical API — Polymarket market/event/user history."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
import json
from typing import Any, Literal

from pmxt.models import Trade

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.Events import fetchEvent, fetchMarket, fetchMarkets
from unipmx.Events.helpers import market_condition_id, price_points_from_history, primary_outcome_id
from unipmx.Events.polymarket import call_polymarket
from unipmx.models import HistoricalValuePoint, OhlcvFrame, PricePoint, UserPnL, UserTradeRecord, UserWalletConnection
from unipmx.Users import fetchUserPnL, fetchUserWalletConnections
from unipmx.Users.polymarket import get_json, normalize_trade, sort_trades

from .ohlcv import fetchOhlcv
from .utils import _RESOLUTION_SECONDS


def _polymarket_only(exchange: str) -> bool:
    return exchange == "Polymarket"


def _to_ts(value: str | int | float | datetime | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        dt = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return int(dt.timestamp())
    if isinstance(value, (int, float)):
        return int(value / 1000 if value > 1e12 else value)
    text = str(value).strip()
    if text.isdigit():
        ts = int(text)
        return int(ts / 1000 if ts > 1e12 else ts)
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp())


def _now_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def _loads_list(value: Any) -> list:
    if isinstance(value, list):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return []
        return parsed if isinstance(parsed, list) else []
    return []


def _market_ref(market_id: str, *, exchange: str) -> dict[str, Any] | None:
    if not _polymarket_only(exchange):
        return None

    try:
        market = fetchMarket(market_id, exchange=exchange)
        yes_id = primary_outcome_id(market)
        no_id = market.no.outcome_id if market.no else None
        return {
            "market_id": market.market_id,
            "condition_id": market_condition_id(market),
            "yes_id": yes_id,
            "no_id": no_id,
            "market": market,
            "raw": market.source_metadata or {},
        }
    except Exception:
        pass

    raw = get_json("https://gamma-api.polymarket.com", f"/markets/{market_id}")
    if not isinstance(raw, dict):
        return None
    token_ids = _loads_list(raw.get("clobTokenIds"))
    return {
        "market_id": str(raw.get("id") or market_id),
        "condition_id": raw.get("conditionId") or raw.get("condition_id") or market_id,
        "yes_id": str(token_ids[0]) if token_ids else None,
        "no_id": str(token_ids[1]) if len(token_ids) > 1 else None,
        "market": None,
        "raw": raw,
    }


def _price_history(
    market_id: str,
    *,
    interval: str,
    start: str | int | datetime | None,
    end: str | int | datetime | None,
    limit: int | None,
    exchange: str,
) -> list[PricePoint]:
    if not _polymarket_only(exchange):
        return []

    ref = _market_ref(market_id, exchange=exchange)
    if not ref or not ref["yes_id"]:
        return []
    yes_id = ref["yes_id"]
    no_id = ref["no_id"]
    params: dict[str, Any] = {"market": yes_id, "interval": interval}
    start_ts = _to_ts(start)
    end_ts = _to_ts(end)
    if start_ts is not None:
        params["startTs"] = start_ts
    if end_ts is not None:
        params["endTs"] = end_ts

    client = getClient(exchange)
    yes_raw = call_polymarket(client, "getPricesHistory", params)
    history = yes_raw.get("history", []) if isinstance(yes_raw, dict) else []
    no_history = None
    if no_id:
        no_params = {**params, "market": no_id}
        try:
            no_raw = call_polymarket(client, "getPricesHistory", no_params)
            no_history = no_raw.get("history", []) if isinstance(no_raw, dict) else []
        except Exception:
            no_history = None
    points = price_points_from_history(history, no_history=no_history, source=exchange)
    if limit is not None:
        return points[-limit:]
    return points


@spun()
def fetchHistoricalMarketPrice(
    market_id: str,
    *,
    interval: str = "1h",
    start: str | int | datetime | None = None,
    end: str | int | datetime | None = None,
    limit: int | None = 100,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[PricePoint]:
    """Historical YES/NO price points for a market."""
    return _price_history(
        market_id,
        interval=interval,
        start=start,
        end=end,
        limit=limit,
        exchange=exchange,
    )


@spun()
def fetchHistoricalMarketPriceOhlcv(
    market_id: str,
    *,
    resolution: str = "1h",
    limit: int | None = 100,
    start: datetime | None = None,
    end: datetime | None = None,
    exchange: str = DEFAULT_EXCHANGE,
) -> OhlcvFrame:
    """Historical OHLCV candles for a market's primary outcome."""
    if not _polymarket_only(exchange):
        return OhlcvFrame([])
    ref = _market_ref(market_id, exchange=exchange)
    if not ref or not ref["yes_id"]:
        return OhlcvFrame([])
    return fetchOhlcv(
        ref["yes_id"],
        resolution=resolution,
        limit=limit,
        start=start,
        end=end,
        market=ref["market"],
        source="trades",
        exchange=exchange,
    )


@spun()
def fetchHistoricalMarketTrades(
    market_id: str,
    *,
    limit: int | None = 100,
    start: str | int | datetime | None = None,
    end: str | int | datetime | None = None,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[Trade]:
    """Historical trades for a market's primary outcome."""
    if not _polymarket_only(exchange):
        return []
    ref = _market_ref(market_id, exchange=exchange)
    if not ref or not ref["yes_id"]:
        return []
    client = getClient(exchange)
    kwargs: dict[str, Any] = {}
    if limit is not None:
        kwargs["limit"] = limit
    if start is not None:
        kwargs["start"] = start.isoformat() if isinstance(start, datetime) else start
    if end is not None:
        kwargs["end"] = end.isoformat() if isinstance(end, datetime) else end
    return client.fetch_trades(ref["yes_id"], **kwargs)


@spun()
def fetchHistoricalMarketVolume(
    market_id: str,
    *,
    resolution: str = "1d",
    limit: int = 30,
    start: str | int | datetime | None = None,
    end: str | int | datetime | None = None,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[HistoricalValuePoint]:
    """Historical market volume buckets, aggregated from trades."""
    if not _polymarket_only(exchange):
        return []
    trades = fetchHistoricalMarketTrades(
        market_id,
        limit=None,
        start=start,
        end=end,
        exchange=exchange,
    )
    bucket_seconds = _RESOLUTION_SECONDS.get(resolution, 86400)
    buckets: dict[int, float] = defaultdict(float)
    for trade in trades:
        ts = int((trade.timestamp / 1000) if trade.timestamp > 1e12 else trade.timestamp)
        bucket = (ts // bucket_seconds) * bucket_seconds
        buckets[bucket] += float(trade.amount or 0) * float(trade.price or 0)
    points = [
        HistoricalValuePoint(timestamp=ts, value=value, kind="volume", raw={"resolution": resolution})
        for ts, value in sorted(buckets.items())
    ]
    return points[-limit:]


@spun()
def fetchHistoricalMarketOpenInterest(
    market_id: str,
    *,
    limit: int = 1,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[HistoricalValuePoint]:
    """Open-interest snapshot for a market.

    Polymarket's public Data API exposes current OI; full historical OI is not
    available from the public endpoint yet.
    """
    if not _polymarket_only(exchange):
        return []
    ref = _market_ref(market_id, exchange=exchange)
    if not ref:
        return []
    raw = get_json("https://data-api.polymarket.com", "/oi", {"market": ref["condition_id"]})
    rows = raw if isinstance(raw, list) else [raw]
    points: list[HistoricalValuePoint] = []
    for row in rows:
        if isinstance(row, dict):
            value = row.get("value") or row.get("openInterest") or row.get("oi")
        else:
            value = row
        try:
            f_value = float(value) if value is not None else None
        except (TypeError, ValueError):
            f_value = None
        points.append(HistoricalValuePoint(timestamp=_now_ts(), value=f_value, kind="open_interest", raw=row if isinstance(row, dict) else {"value": row}))
    return points[:limit]


@spun()
def fetchHistoricalEventPrice(
    event_id: str,
    *,
    interval: str = "1h",
    limit: int | None = 100,
    exchange: str = DEFAULT_EXCHANGE,
) -> dict[str, list[PricePoint]]:
    """Historical prices for every market in an event."""
    if not _polymarket_only(exchange):
        return {}
    event = fetchEvent(event_id, exchange=exchange)
    markets = event.markets or fetchMarkets(event_id=event_id, limit=100, exchange=exchange)
    return {
        market.market_id: fetchHistoricalMarketPrice(
            market.market_id,
            interval=interval,
            limit=limit,
            exchange=exchange,
        )
        for market in markets
    }


@spun()
def fetchHistorical(
    id: str,
    *,
    target: Literal["market", "event", "user"] = "market",
    kind: str = "price",
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
):
    """Generic historical dispatcher."""
    if target == "market":
        if kind in ("price", "prices"):
            return fetchHistoricalMarketPrice(id, exchange=exchange, **kwargs)
        if kind in ("ohlcv", "price_ohlcv"):
            return fetchHistoricalMarketPriceOhlcv(id, exchange=exchange, **kwargs)
        if kind == "volume":
            return fetchHistoricalMarketVolume(id, exchange=exchange, **kwargs)
        if kind in ("trades", "trade_history"):
            return fetchHistoricalMarketTrades(id, exchange=exchange, **kwargs)
        if kind in ("oi", "open_interest"):
            return fetchHistoricalMarketOpenInterest(id, exchange=exchange, **kwargs)
    if target == "event":
        return fetchHistoricalEventPrice(id, exchange=exchange, **kwargs)
    if target == "user":
        if kind in ("trades", "trade_history"):
            return fetchHistoricalUserTradeHistory(id, exchange=exchange, **kwargs)
        if kind in ("pnl", "profit"):
            return fetchHistoricalUserPnl(id, exchange=exchange, **kwargs)
        if kind in ("connections", "wallet_connections"):
            return fetchHistoricalUserWalletConnections(id, exchange=exchange, **kwargs)
    raise ValueError(f"Unsupported historical target={target!r} kind={kind!r}")


@spun()
def fetchHistoricalUserTradeHistory(
    user_address: str,
    *,
    market_id: str | None = None,
    sort: str | None = "newest",
    limit: int = 100,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserTradeRecord]:
    """Historical user trade history."""
    if not _polymarket_only(exchange):
        return []
    raw = get_json("https://data-api.polymarket.com", "/trades", {"user": user_address, "market": market_id, "limit": limit})
    rows = raw if isinstance(raw, list) else []
    trades = [normalize_trade(user_address, row) for row in rows]
    return sort_trades(trades, sort)[:limit]


@spun()
def fetchHistoricalUserPnl(
    user_address: str,
    *,
    window: str = "all",
    exchange: str = DEFAULT_EXCHANGE,
) -> UserPnL | None:
    """Historical user PnL wrapper."""
    if not _polymarket_only(exchange):
        return None
    return fetchUserPnL(user_address, window=window, exchange=exchange)


@spun()
def fetchHistoricalUserWalletConnections(
    user_address: str,
    *,
    limit: int = 20,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserWalletConnection]:
    """Historical-light wallet connections endpoint with limit."""
    if not _polymarket_only(exchange):
        return []
    return fetchUserWalletConnections(user_address, limit=limit, exchange=exchange)
