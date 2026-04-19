# Unimarkets

Unified Python client for prediction markets. Same conventions, one interface.

<p align="center">
  <img src="assets/polymarket.png" width="120" alt="Polymarket"/>
  &nbsp;&nbsp;
  <img src="assets/kalshi.png" width="120" alt="Kalshi"/>
  &nbsp;&nbsp;
  <img src="assets/limitless.png" width="120" alt="Limitless"/>
  &nbsp;&nbsp;
  <img src="assets/gemini.png" width="120" alt="Gemini"/>
</p>

-----

## Install

```
pip install polymwk kalmwk limitlessmwk geminimwk unimarkets
```

## Usage

### Single platform

```python
from polymwk import PolymarketClient
from kalmwk import KalshiClient
from limitlessmwk import LimitlessClient
from geminimwk import GeminiClient

poly   = PolymarketClient()
kalshi = KalshiClient(api_key="...", private_key="...")
lmts   = LimitlessClient(api_key="...", secret="...")
gemini = GeminiClient(api_key="...", secret="...")

markets = poly.fetchMarkets(query="bitcoin")
book    = kalshi.fetchOrderBook(markets[0])
```

### Unified

```python
from unimarkets import UnimarketsClient

uni = UnimarketsClient(poly, kalshi, lmts, gemini)

markets = uni.fetchMarkets(query="bitcoin")           # all platforms
markets = uni.fetchMarkets(query="bitcoin", sources=[poly, kalshi])  # selective
```

## Platforms

|Client            |Platform  |Auth          |Docs                                              |
|------------------|----------|--------------|--------------------------------------------------|
|`PolymarketClient`|Polymarket|None / wallet |[docs](https://docs.polymarket.com)               |
|`KalshiClient`    |Kalshi    |RSA           |[docs](https://trading.kalshi.com/docs/api)       |
|`LimitlessClient` |Limitless |HMAC + EIP-712|[docs](https://docs.limitless.exchange)           |
|`GeminiClient`    |Gemini    |API key       |[docs](https://docs.gemini.com/prediction-markets)|

## Packages

Each client is a standalone pip-installable package. `unimarkets` is the optional unified layer on top.

```
unimarkets/
├── polymwk/        → github.com/MwkosP/Polymwk
├── kalmwk/         → github.com/MwkosP/Kalmwk
├── limitlessmwk/   → github.com/MwkosP/Limitlessmwk
└── geminimwk/      → github.com/MwkosP/Geminimwk
```

## Unsupported methods

```python
kalshi.capabilities  # → {"fetchUserPositions": False, ...}
kalshi.fetchUserPositions()  # → raises NotSupported
```

## Python

3.12+