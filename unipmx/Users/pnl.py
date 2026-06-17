"""Public Users API — PnL and ranking."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserLeaderboardEntry, UserPnL, UserRank

from .polymarket import aggregate_pnl, fetch_leaderboard, polymarket_supported
from .positions import fetchUserPositions


@spun()
def fetchUserPnL(
    address: str,
    window: str = "all",
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UserPnL | None:
    if not polymarket_supported(exchange):
        return None

    open_positions = fetchUserPositions(address, status="open", limit=500, exchange=exchange)
    closed_positions = fetchUserPositions(address, status="closed", limit=500, exchange=exchange)
    return aggregate_pnl(address, window, [*open_positions, *closed_positions])


@spun()
def fetchUsersLeaderboard(
    limit: int = 20,
    window: str = "all",
    by: str = "profit",
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserLeaderboardEntry]:
    if not polymarket_supported(exchange):
        return []
    return fetch_leaderboard(limit, window, by)


@spun()
def fetchUserRank(
    address: str,
    window: str = "all",
    by: str = "profit",
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UserRank | None:
    if not polymarket_supported(exchange):
        return None

    leaderboard = fetchUsersLeaderboard(500, window, by, exchange=exchange)
    needle = address.lower()
    for entry in leaderboard:
        if entry.user_address and entry.user_address.lower() == needle:
            value = entry.pnl if by in ("profit", "pnl") else entry.volume
            return UserRank(
                user_address=address,
                rank=entry.rank,
                window=window,
                by=by,
                value=value,
                raw=entry.raw,
            )
    return UserRank(user_address=address, rank=None, window=window, by=by, value=None)
