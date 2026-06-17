"""Public Users API — wallet activity stream."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserActivityItem

from .polymarket import get_json, normalize_activity, polymarket_supported

@spun()
def fetchUserActivity(
    address: str,
    type: str | None = None,
    market_id: str | None = None,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserActivityItem]:
    if not polymarket_supported(exchange):
        return []

    params = {"user": address, "type": type, "market": market_id, "limit": limit}
    raw = get_json("https://data-api.polymarket.com", "/activity", params)
    rows = raw if isinstance(raw, list) else []
    items = [normalize_activity(address, row) for row in rows]
    return sorted(items, key=lambda i: i.timestamp or 0, reverse=True)[:limit]
