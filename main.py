from unipmx.Display import display
from unipmx import All, Kalshi, Polymarket

# Switch venue here only — Polymarket() | Kalshi() | All()
client = Kalshi()


# ── Events ──────────────────────────────────────────────────────────────
display(client.fetchEvents("election", limit=5, sort="volume", status="active"), query="election")
#display(client.fetchEvents(limit=5, status="active"))
#display(client.fetchEvent("31552"))
#display(client.fetchEventComments("31552", limit=20))
#display(client.fetchRelatedEvents("31552", limit=5))

# ── Markets ─────────────────────────────────────────────────────────────
#display(client.fetchMarkets("btc", limit=5, sort="volume", status="active"), query="btc")
#display(client.fetchMarkets(event_id="31552", limit=10))
#display(client.fetchMarket("market_id_here"))
#display(client.fetchMarketsPaginated("btc", limit=10), query="btc")
#display(client.loadMarkets())

# ── Market detail ───────────────────────────────────────────────────────
#_m = client.fetchMarkets("trump", limit=1, status="active")[0]
#display(client.fetchMarketOrderBook(_m.market_id))
#display(client.fetchMarketActivity(_m.market_id, limit=20))
#display(client.fetchMarketTopHolders(_m.market_id))
#display(client.fetchMarketStats(_m.market_id))
#display(client.fetchMarketResolution(_m.market_id))
#display(client.fetchMarketRules(_m.market_id))
#display(client.fetchMarketGraph(_m.market_id, resolution="1d", limit=48))
#display(client.fetchMarketPositions(_m.market_id, limit=20))

# ── Order books ─────────────────────────────────────────────────────────
#display(client.fetchOrderBookByQuery("btc"), query="btc")
#display(client.fetchOrderBooks(["outcome_id_1", "outcome_id_2"]))
# _market, _outcome = client.getOutcomeId("btc")
#display(client.fetchOrderBook(_outcome.outcome_id))

# ── Series (Polymarket: "nfl" / "1" — Kalshi: "FED") ────────────────────
#display(client.fetchSeries(limit=10, status="active"))
#display(client.fetchSeriesMarkets("nfl", limit=10))
#display(client.fetchSeriesEvents("nfl", limit=10))

# ── Filter (local, on data you already fetched) ─────────────────────────
# _markets = client.fetchMarkets("btc", limit=20)
#display(client.filterMarkets(_markets, "bitcoin"))
# _events = client.fetchEvents("election", limit=20)
#display(client.filterEvents(_events, "president"))

# ── Cross-exchange (client = All() only) ─────────────────────────────────
#display(client.fetchMarkets("bitcoin", limit=20, sort="volume"))
#display(client.fetchEvents("iran", limit=5, sort="volume"))
#display(client.fetchSeries("election", limit=5))
#display(client.fetchMatchedMarkets("btc", limit=10))
#display(client.fetchMatchedPrices("btc", limit=10))
#display(client.fetchArbitrage("btc", limit=10))
# Subset: client = All(("Polymarket", "Kalshi"))
