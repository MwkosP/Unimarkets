"""Public Users API — user trade history."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserTradeRecord

from .polymarket import get_json, normalize_trade, polymarket_supported, sort_trades


@spun()
def fetchUserTrades(
    address: str,
    market_id: str | None = None,
    sort: str | None = None,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserTradeRecord]:
    if not polymarket_supported(exchange):
        return []

    params = {"user": address, "market": market_id, "limit": limit}
    raw = get_json("https://data-api.polymarket.com", "/trades", params)
    rows = raw if isinstance(raw, list) else []
    trades = [normalize_trade(address, row) for row in rows]
    trades = sort_trades(trades, sort)
    return trades[:limit]
