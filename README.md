# unipmx

Unified Python toolkit for prediction markets. One client API, multiple venues, terminal display built in.  
Powered by [pmxt](https://github.com/pmxt-dev/pmxt).

<p align="center">
  <img src="artifacts/imgs/Polymarket.jpeg" width="100" alt="Polymarket"/>
  &nbsp;&nbsp;&nbsp;
  <img src="artifacts/imgs/Kalshi.png" width="100" alt="Kalshi"/>
  &nbsp;&nbsp;&nbsp;
  <img src="artifacts/imgs/Limitless.jpeg" width="100" alt="Limitless"/>
  &nbsp;&nbsp;&nbsp;
  <img src="artifacts/imgs/Gemini.jpeg" width="100" alt="Gemini"/>
</p>
---

## Install

```bash
uv add unipmx
```

You can also clone the repo if you want to run or edit the source locally:

```bash
git clone <your-repo>
cd PM
uv sync
```

## Quick start

Pick a venue once — everything else stays the same:

```python
from unipmx import Polymarket, Kalshi, All
from unipmx.Display import display

client = Polymarket()   # or Kalshi() or All()

display(client.fetchMarkets("btc", limit=5, sort="volume", status="active"), query="btc")
display(client.fetchEvents("election", limit=5, sort="volume", status="active"), query="election")
```

See `[main.py](main.py)` for the full playground.

### Single venue

```python
from unipmx import Polymarket
from unipmx.Display import display

client = Polymarket()

markets = client.fetchMarkets("bitcoin", limit=10, status="active")
event   = client.fetchEvent("31552")
book    = client.fetchMarketOrderBook(markets[0].market_id)

display(markets, query="bitcoin")
display(client.fetchMarketActivity(markets[0].market_id, limit=20))
```

### Cross-exchange

```python
from unipmx import All
from unipmx.Display import display

client = All()   # all venues — or All(("Polymarket", "Kalshi"))

display(client.fetchMarkets("bitcoin", limit=20, sort="volume"))
display(client.fetchEvents("iran", limit=5, sort="volume"))
display(client.fetchMatchedMarkets("btc", limit=10))
display(client.fetchArbitrage("btc", limit=10))
```

## Platforms


| Client         | Platform                                | Auth                                |
| -------------- | --------------------------------------- | ----------------------------------- |
| `Polymarket()` | [Polymarket](https://polymarket.com)    | None / wallet                       |
| `Kalshi()`     | [Kalshi](https://kalshi.com)            | API key + private key (order books) |
| `Limitless()`  | [Limitless](https://limitless.exchange) | API key                             |
| `Myriad()`     | Myriad                                  | —                                   |
| `Probable()`   | Probable                                | —                                   |
| `Smarkets()`   | Smarkets                                | —                                   |
| `All()`        | Every venue above                       | Per-venue                           |


## API surface

### Events

Markets, events, series, order books, filters, and market detail — all camelCase on the client:

```python
client.fetchMarkets(query, limit=10, sort="volume", status="active")
client.fetchEvents(query, limit=10)
client.fetchEvent(event_id)
client.fetchEventComments(event_id, limit=20)      # Polymarket
client.fetchRelatedEvents(event_id, limit=10)

client.fetchSeries(limit=10)
client.fetchSeriesMarkets("nfl", limit=10)           # Polymarket: "nfl" / "1" — Kalshi: "FED"
client.fetchSeriesEvents("nfl", limit=10)

client.fetchMarketOrderBook(market_id)
client.fetchMarketActivity(market_id, limit=20)
client.fetchMarketStats(market_id)
client.fetchMarketGraph(market_id, resolution="1d", limit=48)
client.fetchOrderBookByQuery("btc")
```

### Historical · Users · Feed · Plots

```python
from unipmx.Historical import fetchOhlcv
from unipmx.Users import fetchUserActivity
from unipmx.Feed import watchAddress
from unipmx.Plots import plotChart

display(fetchUserActivity("0x..."), address="0x...")
display(watchAddress("0x...", types=["trades", "positions"]))
plotChart(fetchOhlcv(...), style="candles")
```

## Display

One function renders any return type to a bordered terminal panel:

```python
from unipmx.Display import display

display(client.fetchMarkets("btc", limit=5), query="btc")
display(client.fetchEventComments("31552", limit=20))
display(client.fetchMarketStats(market_id))
```

Event comments render as a chat thread (replies, `@mentions`, reactions).

## Venue notes


| Feature                        | Polymarket     | Kalshi               |
| ------------------------------ | -------------- | -------------------- |
| Series ids                     | `"nfl"`, `"1"` | `"FED"`              |
| Event comments                 | Yes            | — (returns `[]`)     |
| Top holders / market positions | Yes            | — (returns `[]`)     |
| Order book                     | Public         | Requires credentials |


Some methods return empty lists on venues without that API instead of raising.

## Project layout

```
unipmx/
├── clients/       # Polymarket(), Kalshi(), All(), …
├── Events/        # REST — markets, events, series, order books
├── Historical/    # OHLCV, trade history
├── Users/         # Wallet trades, positions, balance
├── Feed/          # WebSocket watches
├── Display/       # display() — unified terminal renderer
└── Plots/         # Browser / terminal charts
```

## Env

```bash
# Optional — hosted user endpoints (Polymarket wallet tracking)
export PMXT_API_KEY=your_key
```

## Python

3.12+