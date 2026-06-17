from unipmx.Display import display
from unipmx import All, Kalshi, Polymarket

# Switch venue here only — Polymarket() | Kalshi() | All()
client = Polymarket()



# ────────────────────────────────────────────────────────────────────────
# Events/
# ────────────────────────────────────────────────────────────────────────

# ── Events ──────────────────────────────────────────────────────────────
#display(client.fetchEvents("election", limit=1, sort="volume", status="active"), query="election")
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





# ────────────────────────────────────────────────────────────────────────
# Users/
# ────────────────────────────────────────────────────────────────────────

# ── Users/ module (Polymarket user tracking; other venues return []/None) ─
#_user = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"

# Profile / portfolio
#display(client.fetchUserProfile(_user))
#display(client.fetchUserWalletAge(_user))
#display(client.fetchUserWalletConnections(_user, limit=20))
#display(client.fetchUserPortfolioValue(_user))
#display(client.fetchUserPnL(_user, window="all"))

# Positions / trades / activity
#display(client.fetchUserPositions(_user, status="open", sort="value", limit=20))
#display(client.fetchUserTrades(_user, market_id=None, sort="newest", limit=20))
#display(client.fetchUserActivity(_user, type=None, market_id=None, limit=20))
#display(client.fetchUserMarkets(_user, status=None, limit=20))

# Rankings / leaderboard
#display(client.fetchUserRank(_user, window="all", by="profit"))
#display(client.fetchUsersLeaderboard(limit=20, window="all", by="profit"))

# Social graph (currently empty unless a venue exposes this)
#display(client.fetchUserFollowers(_user, limit=20))
#display(client.fetchUserFollowing(_user, limit=20))


# ────────────────────────────────────────────────────────────────────────
# Platform/
# ────────────────────────────────────────────────────────────────────────

#display(client.fetchPlatformStats())
#display(client.fetchPlatformFees(limit=20))
#display(client.fetchPlatformCategories(limit=50))
#display(client.fetchPlatformStatus())
#display(client.fetchPlatformVenues())



# ────────────────────────────────────────────────────────────────────────
# Historical/
# ────────────────────────────────────────────────────────────────────────

#_market = client.fetchMarkets("btc", limit=1, status="active")[0]
#_event = client.fetchEvents("election", limit=1, status="active")[0]
#_user = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"

# Market history
#display(client.fetchHistoricalMarketPrice(_market.market_id, interval="1h", limit=100))
#display(client.fetchHistoricalMarketPriceOhlcv(_market.market_id, resolution="1h", limit=48))
#display(client.fetchHistoricalMarketVolume(_market.market_id, resolution="1d", limit=30))
##display(client.fetchHistoricalMarketOpenInterest(_market.market_id))

# Event history
#display(client.fetchHistoricalEventPrice(_event.id, interval="1h", limit=50))

# Generic dispatcher
#display(client.fetchHistorical(_market.market_id, target="market", kind="price", limit=50))

# User historical analysis
#display(client.fetchHistoricalUserTradeHistory(_user, market_id=None, limit=100))
#display(client.fetchHistoricalUserPnl(_user, window="all"))
#display(client.fetchHistoricalUserWalletConnections(_user, limit=20))



# ────────────────────────────────────────────────────────────────────────
# Feed/
# ────────────────────────────────────────────────────────────────────────

# Feed functions are WebSocket subscriptions. Keep one uncommented at a time.

# ── Live public streams ─────────────────────────────────────────────────
_outcome_id = "47412480335198237578326040501125372129499326945928052883104695044572518429794"
#display(client.watchTrades(_outcome_id, limit=20,timeout=10))
#display(client.firehose(venues=["polymarket"]))

# ── Live order books ────────────────────────────────────────────────────
display(client.watchOrderBook(_outcome_id, limit=50))
#display(client.watchOrderBooks(["outcome_id_1", "outcome_id_2"]))
#display(client.watchAllOrderBooks(venues=["polymarket"]))
#client.unwatchOrderBook(_outcome_id)

# ── Wallet/address feed ─────────────────────────────────────────────────
#_feed_user = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"
#display(client.watchAddress(_feed_user))
#display(client.watchAddress(_feed_user, types=["trades", "positions"]))
#client.unwatchAddress(_feed_user)

# ── Authenticated user streams ──────────────────────────────────────────
#display(client.watchUserPositions(wallet_address=_feed_user))
#display(client.watchUserTransactions(wallet_address=_feed_user))

# ── Market price stream ─────────────────────────────────────────────────
#display(client.watchPrices("market_address_here"))







#_market, _outcome = client.getOutcomeId("btc", outcome_index=0)
#print(_outcome.outcome_id)





# ────────────────────────────────────────────────────────────────────────
# Cross-exchange-funcs/
# ────────────────────────────────────────────────────────────────────────
# ── Cross-exchange (client = All() only) ─────────────────────────────────
#display(client.fetchMarkets("bitcoin", limit=20, sort="volume"))
#display(client.fetchEvents("iran", limit=5, sort="volume"))
#display(client.fetchSeries("election", limit=5))
#display(client.fetchMatchedMarkets("btc", limit=10))
#display(client.fetchMatchedPrices("btc", limit=10))
#display(client.fetchArbitrage("btc", limit=10))
# Subset: client = All(("Polymarket", "Kalshi"))


# ── Filter (local, on data you already fetched) ─────────────────────────
# _markets = client.fetchMarkets("btc", limit=20)
#display(client.filterMarkets(_markets, "bitcoin"))
# _events = client.fetchEvents("election", limit=20)
#display(client.filterEvents(_events, "president"))

