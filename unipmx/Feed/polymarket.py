"""Direct Polymarket WebSocket helpers."""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any

import websockets
from pmxt.models import Trade

from unipmx.models import FeedError

POLYMARKET_MARKET_WS = "wss://ws-subscriptions-clob.polymarket.com/ws/market"


def _as_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _as_int(value: Any) -> int:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return int(time.time())


def _trade_from_event(raw: dict[str, Any]) -> Trade:
    side = str(raw.get("side") or "unknown").lower()
    if side not in {"buy", "sell"}:
        side = "unknown"
    timestamp = raw.get("timestamp") or raw.get("time") or int(time.time())
    trade_id = raw.get("id") or raw.get("transaction_hash") or raw.get("hash") or f"{timestamp}:{raw.get('asset_id')}"
    return Trade(
        id=str(trade_id),
        timestamp=_as_int(timestamp),
        price=_as_float(raw.get("price")),
        amount=_as_float(raw.get("size") or raw.get("amount")),
        side=side,  # type: ignore[arg-type]
    )


async def _watch_trades_async(
    outcome_id: str,
    *,
    limit: int,
    timeout: float,
) -> list[Trade]:
    trades: list[Trade] = []
    deadline = time.monotonic() + timeout
    subscribe = {
        "type": "market",
        "assets_ids": [str(outcome_id)],
        "custom_feature_enabled": True,
    }

    async with websockets.connect(POLYMARKET_MARKET_WS, open_timeout=timeout) as ws:
        await ws.send(json.dumps(subscribe))
        while len(trades) < limit and time.monotonic() < deadline:
            try:
                wait_for = max(0.1, min(10, deadline - time.monotonic()))
                message = await asyncio.wait_for(ws.recv(), timeout=wait_for)
            except TimeoutError:
                if time.monotonic() < deadline:
                    await ws.send("PING")
                continue

            if isinstance(message, bytes):
                message = message.decode("utf-8")
            if message in {"PONG", "PING"}:
                continue

            try:
                payload = json.loads(message)
            except json.JSONDecodeError:
                continue

            events = payload if isinstance(payload, list) else [payload]
            for event in events:
                if not isinstance(event, dict):
                    continue
                if event.get("event_type") != "last_trade_price":
                    continue
                trades.append(_trade_from_event(event))
                if len(trades) >= limit:
                    break
    return trades


def watch_polymarket_trades(
    outcome_id: str,
    *,
    limit: int | None = None,
    timeout: float = 20,
) -> list[Trade] | FeedError:
    wanted = limit or 1
    try:
        return asyncio.run(_watch_trades_async(outcome_id, limit=wanted, timeout=timeout))
    except Exception as exc:  # noqa: BLE001 - surface feed failures as data.
        return FeedError(
            function="watchTrades",
            message=str(exc),
            exchange="Polymarket",
            hint=(
                "Direct Polymarket WebSocket failed. Check VPN/network WebSocket access to "
                "wss://ws-subscriptions-clob.polymarket.com/ws/market."
            ),
            raw={"error_type": type(exc).__name__},
        )
