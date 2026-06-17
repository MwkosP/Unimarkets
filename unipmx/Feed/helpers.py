"""Helpers for WebSocket feed wrappers."""

from __future__ import annotations

from typing import Callable, TypeVar

from pmxt.errors import PmxtError

from unipmx.models import FeedError

T = TypeVar("T")


def feed_hint(message: str) -> str:
    if "requires WebSocket transport" in message or "connection failed" in message:
        return (
            "This Feed function is WebSocket-only. Make sure the pmxt sidecar can open "
            "WebSocket connections and that your network/VPN is not blocking Polymarket/Kalshi streams."
        )
    return "The WebSocket feed call failed before data was returned."


def safe_feed(function: str, exchange: str, call: Callable[[], T]) -> T | FeedError:
    try:
        return call()
    except PmxtError as exc:
        message = str(exc)
        return FeedError(
            function=function,
            message=message,
            exchange=exchange,
            hint=feed_hint(message),
            raw={"error_type": type(exc).__name__},
        )
