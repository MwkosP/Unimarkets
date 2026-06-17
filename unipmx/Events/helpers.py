"""Shared venue helpers for Events market/event detail."""

from __future__ import annotations

from typing import Any

from pmxt.models import Trade, UnifiedEvent, UnifiedMarket

from unipmx.models import (
    Comment,
    Holder,
    MarketPosition,
    MarketRules,
    MarketStats,
    PricePoint,
    Resolution,
)


def market_condition_id(market: UnifiedMarket) -> str:
    return market.contract_address or market.market_id


def primary_outcome_id(market: UnifiedMarket) -> str:
    if market.yes:
        return market.yes.outcome_id
    return market.outcomes[0].outcome_id


def normalize_comment(raw: dict, *, source: str) -> Comment:
    profile = raw.get("profile") or {}
    author = profile.get("name") or profile.get("pseudonym") or raw.get("userAddress")
    parent_id = raw.get("parentCommentID")
    return Comment(
        id=str(raw.get("id", "")),
        body=raw.get("body") or "",
        author=author,
        created_at=raw.get("createdAt"),
        source=source,
        raw=raw,
        parent_comment_id=str(parent_id) if parent_id is not None else None,
        reaction_count=int(raw.get("reactionCount") or 0),
    )


def normalize_holder(raw: dict, *, outcome: str | None, source: str) -> Holder:
    return Holder(
        address=raw.get("proxyWallet") or raw.get("address") or "",
        amount=float(raw.get("amount") or 0),
        outcome=outcome,
        name=raw.get("name") or raw.get("pseudonym"),
        source=source,
        raw=raw,
    )


def normalize_trade(raw: dict, *, source: str) -> Trade:
    ts = raw.get("timestamp") or raw.get("createdAt") or 0
    if isinstance(ts, str):
        from datetime import datetime

        try:
            ts = int(datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp() * 1000)
        except ValueError:
            ts = 0
    price = float(raw.get("price") or raw.get("avgPrice") or 0)
    amount = float(raw.get("size") or raw.get("amount") or 0)
    side = raw.get("side") or "unknown"
    if side not in ("buy", "sell"):
        side = "unknown"
    trade_id = str(raw.get("id") or raw.get("transactionHash") or f"{ts}-{price}")
    return Trade(id=trade_id, timestamp=int(ts), price=price, amount=amount, side=side)


def normalize_position(raw: dict, *, source: str) -> MarketPosition:
    return MarketPosition(
        address=raw.get("proxyWallet") or raw.get("address") or "",
        outcome=raw.get("outcome"),
        size=float(raw.get("size") or 0),
        avg_price=float(raw["avgPrice"]) if raw.get("avgPrice") is not None else None,
        current_value=float(raw["currentValue"]) if raw.get("currentValue") is not None else None,
        source=source,
        raw=raw,
    )


def market_stats_from(
    market: UnifiedMarket,
    *,
    exchange: str,
    extra: dict | None = None,
) -> MarketStats:
    meta = market.source_metadata or {}
    oi = market.open_interest
    if extra and not oi:
        oi_val = extra.get("value")
        if oi_val is not None:
            oi = float(oi_val)
    if exchange == "Kalshi" and not oi:
        oi_raw = meta.get("open_interest") or meta.get("open_interest_fp")
        if oi_raw is not None:
            try:
                oi = float(oi_raw)
            except (TypeError, ValueError):
                pass
    unique = meta.get("uniqueTraders") or meta.get("unique_traders")
    return MarketStats(
        market_id=market.market_id,
        volume=market.volume or market.volume_24h,
        liquidity=market.liquidity,
        open_interest=oi,
        unique_traders=int(unique) if unique is not None else None,
        source=exchange,
        raw={"market": meta, **(extra or {})},
    )


def resolution_from(market: UnifiedMarket, *, exchange: str) -> Resolution:
    meta = market.source_metadata or {}
    outcome = None
    if exchange == "Kalshi":
        outcome = meta.get("result")
        if outcome and str(outcome).lower() in ("", "null", "none"):
            outcome = None
    elif market.outcomes:
        winners = [o.label for o in market.outcomes if o.price is not None and o.price >= 0.99]
        if winners:
            outcome = winners[0]
        elif meta.get("outcome"):
            outcome = str(meta["outcome"])
    status = market.status or meta.get("umaResolutionStatus") or meta.get("status")
    resolved_at = (
        meta.get("closedTime")
        or meta.get("umaEndDate")
        or meta.get("close_time")
        or (str(market.resolution_date) if market.resolution_date else None)
    )
    return Resolution(
        market_id=market.market_id,
        status=status,
        outcome=outcome,
        resolved_by=meta.get("resolvedBy"),
        resolved_at=resolved_at,
        resolution_source=meta.get("resolutionSource") or meta.get("rules_primary"),
        source=exchange,
        raw=meta,
    )


def rules_from(market: UnifiedMarket, *, exchange: str) -> MarketRules:
    meta = market.source_metadata or {}
    criteria = meta.get("groupItemTitle") or meta.get("questionID")
    if exchange == "Kalshi":
        criteria = meta.get("rules_primary") or meta.get("early_close_condition") or criteria
    return MarketRules(
        market_id=market.market_id,
        description=market.description,
        resolution_source=meta.get("resolutionSource") or meta.get("rules_primary"),
        criteria=str(criteria) if criteria else None,
        source=exchange,
        raw=meta,
    )


def price_points_from_history(
    history: list[dict],
    *,
    no_history: list[dict] | None = None,
    source: str,
) -> list[PricePoint]:
    no_by_ts = {int(p["t"]): float(p["p"]) for p in (no_history or []) if "t" in p and "p" in p}
    points: list[PricePoint] = []
    for row in history:
        ts = int(row.get("t", 0))
        yes = float(row["p"]) if row.get("p") is not None else None
        points.append(
            PricePoint(
                timestamp=ts,
                yes_price=yes,
                no_price=no_by_ts.get(ts),
                source=source,
                raw=row,
            )
        )
    return points


def price_points_from_candles(candles, *, exchange: str) -> list[PricePoint]:
    return [
        PricePoint(
            timestamp=int(c.timestamp or 0),
            yes_price=c.close,
            no_price=1.0 - c.close if c.close is not None else None,
            source=exchange,
            raw=None,
        )
        for c in candles
    ]


def related_event_params(event: UnifiedEvent, *, exchange: str) -> dict[str, Any] | None:
    meta = event.source_metadata or {}
    if exchange == "Polymarket":
        tag = event.category or (event.tags[0] if event.tags else None)
        return {"tag": tag} if tag else None
    if exchange == "Kalshi":
        series_ticker = meta.get("series_ticker")
        if series_ticker:
            return {"series_ticker": series_ticker}
    tag = event.category or (event.tags[0] if event.tags else None)
    return {"query": tag} if tag else None
