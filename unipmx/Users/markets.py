"""Public Users API — markets a user participates in."""

from collections import defaultdict

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserMarket

from .polymarket import polymarket_supported
from .positions import fetchUserPositions


@spun()
def fetchUserMarkets(
    address: str,
    status: str | None = None,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserMarket]:
    if not polymarket_supported(exchange):
        return []

    position_status = status or "open"
    positions = fetchUserPositions(
        address,
        status=position_status,
        sort="value",
        limit=max(limit * 4, limit),
        exchange=exchange,
    )

    grouped: dict[str | None, list] = defaultdict(list)
    for pos in positions:
        grouped[pos.market_id].append(pos)

    markets: list[UserMarket] = []
    for market_id, rows in grouped.items():
        current_value = sum(p.current_value or 0 for p in rows)
        cash_pnl = sum(p.cash_pnl or 0 for p in rows)
        size = sum(p.size for p in rows)
        markets.append(
            UserMarket(
                user_address=address,
                market_id=market_id,
                title=rows[0].title,
                outcomes=[p.outcome or "" for p in rows if p.outcome],
                size=size,
                current_value=current_value,
                cash_pnl=cash_pnl,
                status=position_status,
                raw={"positions": [p.raw for p in rows]},
            )
        )

    return sorted(markets, key=lambda m: m.current_value or 0, reverse=True)[:limit]
