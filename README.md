# Unimarkets

Unified Python client for prediction markets. Same conventions, one interface.

<p align="center">
  <img src="IMG_2216.jpeg" width="80" alt="Polymarket"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/kalshi.png" width="80" alt="Kalshi"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/limitless.png" width="80" alt="Limitless"/>
  &nbsp;&nbsp;&nbsp;
  <img src="assets/gemini.png" width="80" alt="Gemini"/>
</p>

-----

## Install

```
uv add unimarkets
```

## Usage

### Single platform

```python
from unimarkets import PolymarketClient, KalshiClient, LimitlessClient, GeminiClient

poly   = PolymarketClient()
kalshi = KalshiClient(api_key="...", private_key="...")
lmts   = LimitlessClient(api_key="...", secret="...")
gemini = GeminiClient(api_key="...", secret="...")

markets = poly.fetchMarkets(query="bitcoin")
book    = poly.fetchOrderBook(markets[0])
```

### Unified

```python
from unimarkets import UnimarketsClient

uni = UnimarketsClient(poly, kalshi, lmts, gemini)

markets = uni.fetchMarkets(query="bitcoin")                            # all
markets = uni.fetchMarkets(query="bitcoin", sources=[poly, kalshi])   # selective
```

## Platforms

|Client            |Platform                               |Auth          |
|------------------|---------------------------------------|--------------|
|`PolymarketClient`|[Polymarket](https://polymarket.com)   |None / wallet |
|`KalshiClient`    |[Kalshi](https://kalshi.com)           |RSA           |
|`LimitlessClient` |[Limitless](https://limitless.exchange)|HMAC + EIP-712|
|`GeminiClient`    |[Gemini](https://gemini.com)           |API key       |

## Unsupported methods

```python
kalshi.capabilities                # → {"fetchUserPositions": False, ...}
kalshi.fetchUserPositions()        # → raises NotSupported
```

## Python

3.12+