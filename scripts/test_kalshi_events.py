#!/usr/bin/env python3
"""Smoke-test all Events/ APIs on Kalshi."""

from unipmx import Kalshi
from unipmx.exceptions import NotSupported

k = Kalshi()
results: list[tuple[str, str, str]] = []


def check(name: str, fn):
    try:
        r = fn()
        detail = len(r) if hasattr(r, "__len__") and not isinstance(r, str) else type(r).__name__
        results.append((name, "OK", str(detail)))
    except NotSupported as e:
        results.append((name, "NotSupported", str(e)[:60]))
    except Exception as e:
        results.append((name, "FAIL", f"{type(e).__name__}: {str(e)[:80]}"))


markets = k.fetchMarkets("trump", limit=2, status="active")
events = k.fetchEvents("fed", limit=2, status="active")
mid = markets[0].market_id if markets else None
eid = events[0].id if events else None

check("fetchMarkets", lambda: k.fetchMarkets("trump", limit=2, status="active"))
check("fetchEvents", lambda: k.fetchEvents("fed", limit=2, status="active"))
if eid:
    check("fetchEvent", lambda: k.fetchEvent(eid))
    check("fetchRelatedEvents", lambda: k.fetchRelatedEvents(eid, limit=3))
    check("fetchEventComments", lambda: k.fetchEventComments(eid, limit=5))
if mid:
    check("fetchMarket", lambda: k.fetchMarket(mid))
    check("fetchMarketStats", lambda: k.fetchMarketStats(mid))
    check("fetchMarketResolution", lambda: k.fetchMarketResolution(mid))
    check("fetchMarketRules", lambda: k.fetchMarketRules(mid))
    check("fetchMarketGraph", lambda: k.fetchMarketGraph(mid, resolution="1d", limit=5))
    check("fetchMarketActivity", lambda: k.fetchMarketActivity(mid, limit=5))
    check("fetchMarketTopHolders", lambda: k.fetchMarketTopHolders(mid))
    check("fetchMarketPositions", lambda: k.fetchMarketPositions(mid, limit=5))
    check("fetchMarketOrderBook", lambda: k.fetchMarketOrderBook(mid))
check("fetchMarketsPaginated", lambda: k.fetchMarketsPaginated("trump", limit=2))
check("fetchSeries", lambda: k.fetchSeries(limit=3))
check("fetchSeriesMarkets", lambda: k.fetchSeriesMarkets("FED", limit=3))
check("fetchSeriesEvents", lambda: k.fetchSeriesEvents("FED", limit=3))
if markets:
    check("filterMarkets", lambda: k.filterMarkets(markets, "trump"))
if events:
    check("filterEvents", lambda: k.filterEvents(list(events), "fed"))
if markets:
  try:
    m, o = k.getOutcomeId("trump", market_index=0, active_only=False)
    check("getOutcomeId", lambda: (m, o))
    check("fetchOrderBook", lambda: k.fetchOrderBook(o.outcome_id))
    check("fetchOrderBooks", lambda: k.fetchOrderBooks([o.outcome_id]))
  except Exception as e:
    results.append(("getOutcomeId", "FAIL", str(e)[:80]))

for name, status, detail in results:
    print(f"{name:25} {status:12} {detail}")

failed = [r for r in results if r[1] == "FAIL"]
raise SystemExit(1 if failed else 0)
