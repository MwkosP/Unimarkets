"""Shared pmxt client factory."""

import os
from typing import Any

from unipmx.config import DEFAULT_EXCHANGE, EXCHANGES


def getClient(
    exchange: str = DEFAULT_EXCHANGE,
    *,
    wallet_address: str | None = None,
    api_key: str | None = None,
) -> Any:
    try:
        cls = EXCHANGES[exchange]
    except KeyError as exc:
        raise ValueError(
            f"Unknown exchange '{exchange}'. Available: {', '.join(EXCHANGES)}"
        ) from exc

    kwargs: dict[str, Any] = {}
    key = api_key or os.environ.get("PMXT_API_KEY")
    if key:
        kwargs["pmxt_api_key"] = key
    if wallet_address:
        kwargs["wallet_address"] = wallet_address

    return cls(**kwargs) if kwargs else cls()
