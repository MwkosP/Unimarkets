# unipmx — Architecture & Naming Rules

## Public API (used by `main.py`)

Every function that `main.py` calls **must**:

1. Be **camelCase** — e.g. `fetchMarkets()`, `runFetchEvents()`
2. Live in a module's top-level `.py` file (not in `utils.py`)
3. Be re-exported from that module's `__init__.py` when part of the public surface

```python
# main.py — fetch from module + display()
from unipmx.Display import display
from unipmx.Events import fetchMarkets, fetchEvents

display(fetchMarkets("btc", limit=5), query="btc", exchange="Polymarket")
display(fetchEvents("election", limit=3), query="election")
```

Do **not** use `Run/` wrappers in main. Call module functions directly.

## Helpers → `utils.py`

Non-public helpers go in `utils.py` inside each module folder (snake_case OK).

## Folder layout

```
unipmx/
├── config.py              # EXCHANGES, defaults
├── client.py              # getClient()
├── models.py              # shared dataclasses
├── Events/                # REST — markets, events, series, order books, filters, router
│   ├── markets.py
│   ├── events.py
│   ├── series.py
│   ├── orderbook.py
│   ├── filter.py
│   ├── router.py
│   └── utils.py
├── Historical/            # REST — OHLCV, market trade history
│   ├── ohlcv.py
│   └── trades.py
├── Users/                 # REST — wallet trades, positions, balance, orders, activity
│   ├── trades.py
│   ├── positions.py
│   ├── balance.py
│   ├── orders.py
│   └── activity.py
├── Feed/                  # WebSocket — order books, trades, wallet watch, user streams
│   ├── orderbook.py
│   ├── trades.py
│   ├── address.py
│   └── user.py
├── Display/               # ONE unified renderer
│   ├── display.py         # display(data) — dispatches to all types
│   └── utils.py           # render helpers (internal)
```

Do **not** add `Run/` or `Compare/` folders. `main.py` calls module APIs + `display()` directly.

## Unified display

```python
from unipmx.Events import fetchEvents, fetchMarkets
from unipmx.Users import fetchUserActivity
from unipmx.Display import display

display(fetchMarkets("btc", limit=5), query="btc", exchange="Polymarket")
display(fetchEvents("election", limit=3), query="election")
display(fetchUserActivity("0x..."), address="0x...")
```

`display()` auto-detects: markets, events, trades, positions, balances, orders, OHLCV, order books, user activity, wallet snapshots, search results, compare dicts.

## Domain map

| Folder | REST / WS | Responsibility |
|--------|-----------|----------------|
| `Events/` | REST | Markets, events, series, order books, filters, cross-venue router |
| `Historical/` | REST | OHLCV candles, market trade history |
| `Users/` | REST | Any wallet: trades, positions, balance, orders, full activity |
| `Feed/` | WebSocket | Live order books, trades, `watchAddress`, user streams |
| `Display/` | — | `display(anything)` |

## Polymarket user tracking

```python
from unipmx.Users import fetchUserActivity, fetchUserTrades, fetchUserPositions
from unipmx.Feed import watchAddress
from unipmx.Display import display

address = "0x..."
display(fetchUserActivity(address))           # trades + positions + balance
display(fetchUserTrades(address, limit=100))  # trade history only
display(watchAddress(address, types=["trades", "positions"]))  # live feed
```

Requires `PMXT_API_KEY` env var for hosted user endpoints.

## Naming

| Layer | Style | Example |
|-------|-------|---------|
| main.py calls | camelCase | `display(fetchMarkets(...))` |
| Public API | camelCase | `fetchUserTrades()` |
| utils.py | snake_case | `to_yes_no_prices()` |
| Module folders | PascalCase | `Events/`, `Users/` |
