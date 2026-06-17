"""Public Users API — user positions."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserPosition

from .polymarket import get_json, normalize_position, polymarket_supported, sort_positions


@spun()
def fetchUserPositions(
    address: str,
    status: str = "open",
    sort: str | None = None,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserPosition]:
    if not polymarket_supported(exchange):
        return []

    endpoint = "/closed-positions" if status == "closed" else "/positions"
    raw = get_json("https://data-api.polymarket.com", endpoint, {"user": address, "limit": limit})
    rows = raw if isinstance(raw, list) else []
    positions = [normalize_position(address, row, status=status) for row in rows]
    positions = sort_positions(positions, sort)
    return positions[:limit]
