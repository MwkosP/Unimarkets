"""Polymarket-specific API helpers via pmxt call_api."""

from __future__ import annotations

from typing import Any


def call_polymarket(client: Any, operation_id: str, params: dict | None = None) -> Any:
    return client.call_api(operation_id, params or {})
