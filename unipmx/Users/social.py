"""Public Users API — social graph.

Polymarket currently exposes public profiles, positions, trades, activity, and
leaderboards, but not a public followers/following graph. These functions are
kept in the unified API and return an empty list until a venue exposes it.
"""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserProfile


@spun()
def fetchUserFollowers(
    address: str,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserProfile]:
    return []


@spun()
def fetchUserFollowing(
    address: str,
    limit: int = 20,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> list[UserProfile]:
    return []
