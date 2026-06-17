"""Public Users API — portfolio value."""

from unipmx.Display.spinner import spun
from unipmx.config import DEFAULT_EXCHANGE
from unipmx.models import UserPortfolioValue

from .polymarket import get_json, polymarket_supported, as_float


@spun()
def fetchUserPortfolioValue(
    address: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
) -> UserPortfolioValue | None:
    if not polymarket_supported(exchange):
        return None

    raw = get_json("https://data-api.polymarket.com", "/value", {"user": address})
    if isinstance(raw, dict):
        value = as_float(raw.get("value") or raw.get("total") or raw.get("portfolioValue"))
    else:
        value = as_float(raw)
    return UserPortfolioValue(user_address=address, value=value, raw=raw if isinstance(raw, dict) else {"value": raw})
