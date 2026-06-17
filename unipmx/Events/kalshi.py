"""Kalshi-specific Events helpers."""

from __future__ import annotations

from typing import Any

from pmxt.models import UnifiedEvent, UnifiedMarket, UnifiedSeries


def series_ticker(series: UnifiedSeries) -> str:
    return series.ticker or series.id


def fetch_series_events(client: Any, series: UnifiedSeries, **kwargs: Any) -> list[UnifiedEvent]:
    ticker = series_ticker(series)
    limit = kwargs.pop("limit", 100)
    return client.fetch_events(series_ticker=ticker, limit=limit, **kwargs)


def fetch_series_markets(client: Any, series: UnifiedSeries, **kwargs: Any) -> list[UnifiedMarket]:
    ticker = series_ticker(series)
    limit = kwargs.pop("limit", 100)
    return client.fetch_markets(series_ticker=ticker, limit=limit, **kwargs)
