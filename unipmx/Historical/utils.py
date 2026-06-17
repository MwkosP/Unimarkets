"""Internal helpers for Historical module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pmxt.models import PriceCandle, UnifiedMarket

# Max window per request (Polymarket enforces interval size per resolution).
_OHLCV_CHUNK: dict[str, tuple[timedelta, int]] = {
    "1m": (timedelta(hours=12), 720),
    "5m": (timedelta(hours=24), 288),
    "15m": (timedelta(hours=48), 192),
    "1h": (timedelta(hours=168), 168),
    "4h": (timedelta(days=14), 84),
    "1d": (timedelta(days=14), 14),
    "max": (timedelta(days=14), 14),
}

# Single-request caps when limit is an int.
_OHLCV_LIMIT_CAP: dict[str, int] = {
    "1d": 14,
    "max": 14,
}


def cap_ohlcv_limit(resolution: str, limit: int) -> int:
    cap = _OHLCV_LIMIT_CAP.get(resolution)
    return min(limit, cap) if cap else limit


def _parse_dt(value: str | datetime | int | float | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        ts = value / 1000 if value > 1e12 else value
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    text = str(value).strip()
    if text.isdigit():
        ts = int(text)
        ts = ts / 1000 if ts > 1e12 else ts
        return datetime.fromtimestamp(ts, tz=timezone.utc)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def market_history_bounds(market: UnifiedMarket) -> tuple[datetime | None, datetime]:
    """Infer OHLCV start/end from market metadata."""
    meta = market.source_metadata or {}
    start: datetime | None = None
    for key in ("createdAt", "startDate", "startDateIso"):
        start = _parse_dt(meta.get(key))
        if start:
            break

    end: datetime | None = None
    for key in ("closedTime", "umaEndDate"):
        end = _parse_dt(meta.get(key))
        if end:
            break
    if end is None and (market.status or "").lower() in ("closed", "resolved", "inactive"):
        end = _parse_dt(market.resolution_date)
    if end is None:
        end = datetime.now(timezone.utc)
    return start, end


def fetch_ohlcv_all(
    client,
    outcome_id: str,
    *,
    resolution: str = "1h",
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[PriceCandle]:
    """Paginate backwards until the full range is covered."""
    chunk_delta, chunk_limit = _OHLCV_CHUNK.get(resolution, (timedelta(hours=168), 168))
    end_dt = end or datetime.now(timezone.utc)
    start_bound = start

    all_candles: list[PriceCandle] = []
    seen: set[int] = set()
    cursor_end = end_dt

    for _ in range(500):  # safety cap
        chunk_start = cursor_end - chunk_delta
        if start_bound and chunk_start < start_bound:
            chunk_start = start_bound

        batch = client.fetch_ohlcv(
            outcome_id,
            resolution=resolution,
            limit=chunk_limit,
            start=chunk_start,
            end=cursor_end,
        )
        new = [c for c in batch if c.timestamp and c.timestamp not in seen]
        if not new:
            break

        new.sort(key=lambda c: c.timestamp or 0)
        all_candles = new + all_candles
        seen.update(c.timestamp for c in new if c.timestamp)

        earliest = datetime.fromtimestamp(new[0].timestamp / 1000, tz=timezone.utc)
        if start_bound and earliest <= start_bound:
            break
        if earliest >= cursor_end:
            break
        cursor_end = earliest
        if len(batch) < 2:
            break

    return all_candles


_RESOLUTION_SECONDS: dict[str, int] = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
    "max": 86400,
}


def resolution_window(resolution: str, limit: int) -> timedelta:
    seconds = _RESOLUTION_SECONDS.get(resolution, 3600) * limit
    return timedelta(seconds=seconds)


def candles_have_bodies(candles: list[PriceCandle]) -> bool:
    return any(c.open != c.close or c.high != c.low for c in candles)


def trades_to_candles(
    trades,
    resolution: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
    limit: int | None = None,
) -> list[PriceCandle]:
    """Build real OHLC candles (doji, wicks, bodies) from trade ticks."""
    from collections import defaultdict

    bucket_ms = _RESOLUTION_SECONDS.get(resolution, 3600) * 1000
    buckets: dict[int, list] = defaultdict(list)
    for trade in sorted(trades, key=lambda t: t.timestamp):
        bucket = (trade.timestamp // bucket_ms) * bucket_ms
        buckets[bucket].append(trade)

    candles: list[PriceCandle] = []
    prev_close: float | None = None
    for ts in sorted(buckets.keys()):
        batch = buckets[ts]
        prices = [t.price for t in batch]
        vol = sum(t.amount for t in batch)
        o = prev_close if prev_close is not None else prices[0]
        c = prices[-1]
        h = max(max(prices), o)
        lo = min(min(prices), o)
        candles.append(PriceCandle(timestamp=ts, open=o, high=h, low=lo, close=c, volume=vol))
        prev_close = c

    if not candles and limit is None:
        return []

    end_dt = end or datetime.now(timezone.utc)
    end_bucket = (int(end_dt.timestamp() * 1000) // bucket_ms) * bucket_ms

    if limit is None:
        if start is not None:
            start_dt = start
        elif candles:
            start_dt = datetime.fromtimestamp(candles[0].timestamp / 1000, tz=timezone.utc)
        else:
            return []
        start_bucket = (int(start_dt.timestamp() * 1000) // bucket_ms) * bucket_ms
    else:
        if not candles:
            return []
        start_bucket = end_bucket - (limit - 1) * bucket_ms

    by_ts = {c.timestamp: c for c in candles}
    seed = next((c for c in candles if c.timestamp <= end_bucket), candles[0])
    prev = seed.close
    filled: list[PriceCandle] = []
    ts = start_bucket
    while ts <= end_bucket:
        if ts in by_ts:
            prev = by_ts[ts].close
            filled.append(by_ts[ts])
        else:
            filled.append(
                PriceCandle(timestamp=ts, open=prev, high=prev, low=prev, close=prev, volume=0)
            )
        ts += bucket_ms
    return filled


def fetch_trades_all(
    client,
    outcome_id: str,
    *,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list:
    """Paginate trade history backwards in time."""
    end_dt = end or datetime.now(timezone.utc)
    start_bound = start or (end_dt - timedelta(days=365))
    chunk = timedelta(days=1)

    all_trades = []
    seen: set[str] = set()
    cursor_end = end_dt

    for _ in range(500):
        if cursor_end <= start_bound:
            break
        cursor_start = max(start_bound, cursor_end - chunk)
        batch = client.fetch_trades(
            outcome_id,
            limit=1000,
            start=cursor_start.isoformat(),
            end=cursor_end.isoformat(),
        )
        new = [t for t in batch if t.id not in seen]
        if not new:
            cursor_end = cursor_start
            continue

        all_trades.extend(new)
        seen.update(t.id for t in new)
        oldest = min(t.timestamp for t in new)
        next_end = datetime.fromtimestamp(oldest / 1000, tz=timezone.utc) - timedelta(milliseconds=1)
        if next_end >= cursor_end:
            cursor_end = cursor_start
        else:
            cursor_end = next_end

    all_trades.sort(key=lambda t: t.timestamp)
    return all_trades
