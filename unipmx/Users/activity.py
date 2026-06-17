"""Public Users API — full wallet snapshot (trades + positions + balance)."""

from dataclasses import dataclass

from pmxt.models import Balance, Position, UserTrade

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE

from .balance import fetchUserBalance
from .positions import fetchUserPositions
from .trades import fetchUserTrades


@dataclass
class UserActivity:
    address: str
    trades: list[UserTrade]
    positions: list[Position]
    balances: list[Balance]


@spun()
def fetchUserActivity(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    trade_limit: int | None = 50,
) -> UserActivity:
    return UserActivity(
        address=address,
        trades=fetchUserTrades(address, exchange=exchange, limit=trade_limit),
        positions=fetchUserPositions(address, exchange=exchange),
        balances=fetchUserBalance(address, exchange=exchange),
    )
