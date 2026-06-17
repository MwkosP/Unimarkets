"""Public Events API — events (REST)."""

from typing import Any

from pmxt.models import UnifiedEvent

from unipmx.Display.spinner import spun
from unipmx.client import getClient
from unipmx.config import DEFAULT_EXCHANGE, DEFAULT_LIMIT, SortKey, StatusKey
from unipmx.models import Comment, EventList

from .helpers import normalize_comment, related_event_params
from .polymarket import call_polymarket
from .support import COMMENTS_VENUES
from .utils import fetch_kwargs, sort_events


@spun()
def fetchEvents(
    query: str | None = None,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    sort: SortKey | None = None,
    status: StatusKey | None = None,
    show_markets: bool = True,
    **kwargs: Any,
) -> EventList:
    params = fetch_kwargs(query or "", limit, sort, status=status)
    if not query:
        params.pop("query", None)
    params.update(kwargs)
    events = getClient(exchange).fetch_events(**params)
    return EventList(sort_events(events, sort), show_markets=show_markets)


@spun()
def fetchEvent(
    event_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> UnifiedEvent:
    return getClient(exchange).fetch_event(event_id=event_id, **kwargs)


@spun()
def fetchEventComments(
    event_id: str,
    limit: int = DEFAULT_LIMIT,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    **kwargs: Any,
) -> list[Comment]:
    """Comments / discussion thread on an event (Polymarket only; empty elsewhere)."""
    if exchange not in COMMENTS_VENUES:
        return []

    raw = call_polymarket(
        getClient(exchange),
        "listComments",
        {
            "parent_entity_id": event_id,
            "parent_entity_type": "Event",
            "limit": limit,
            **kwargs,
        },
    )
    if not isinstance(raw, list):
        return []
    return [normalize_comment(c, source=exchange) for c in raw[:limit]]


@spun()
def fetchRelatedEvents(
    event_id: str,
    *,
    exchange: str = DEFAULT_EXCHANGE,
    limit: int = DEFAULT_LIMIT,
    show_markets: bool = True,
    **kwargs: Any,
) -> EventList:
    """Events in the same topic cluster / category."""
    event = fetchEvent(event_id, exchange=exchange)
    params = related_event_params(event, exchange=exchange)
    if not params:
        return EventList([], show_markets=show_markets)
    related = getClient(exchange).fetch_events(limit=limit + 1, **params, **kwargs)
    return EventList([e for e in related if e.id != event.id][:limit], show_markets=show_markets)
