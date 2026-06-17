"""Public Plots API — plot pre-fetched OHLCV data."""

from __future__ import annotations

from unipmx.config import ChartStyleKey
from unipmx.models import OhlcvCandles, OhlcvFrame, OhlcvSeries

from .browser import plotCandles, plotSeries
from .terminal import plotTerminal


def _as_frame(data: OhlcvFrame | OhlcvCandles) -> OhlcvFrame:
    return data if isinstance(data, OhlcvFrame) else OhlcvFrame(data.candles)


def plotChart(
    data: OhlcvFrame | OhlcvCandles | OhlcvSeries,
    *,
    style: ChartStyleKey = "candles",
    column: str = "close",
    title: str | None = None,
    terminal: bool = False,
) -> None:
    """
    Plot OHLCV data in the browser (TradingView-style).

    Fetch data first with :func:`unipmx.Historical.fetchOhlcv` or
    :func:`unipmx.Historical.fetchOhlcvByQuery`, then pass it here.

    Examples::

        ohlcv = fetchOhlcvByQuery("btc", resolution="1d", limit=None)
        plotChart(ohlcv, style="candles")
        plotChart(ohlcv, style="line")
        plotChart(ohlcv, style="line", column="close")
    """
    if terminal:
        series = _line_series(data, column=column)
        plotTerminal(series, title=title or column.title())
        return

    if style == "candles":
        if isinstance(data, OhlcvSeries):
            raise TypeError('plotChart(style="candles") needs OhlcvFrame, not a single column')
        frame = _as_frame(data)
        plotCandles(frame["ohlc"], title=title or "OHLCV")
        return

    if style == "line":
        series = _line_series(data, column=column)
        plotSeries(series, title=title or series.name.title())
        return

    raise ValueError(f'Unknown style {style!r} — use "candles" or "line"')


def _line_series(
    data: OhlcvFrame | OhlcvCandles | OhlcvSeries,
    *,
    column: str,
) -> OhlcvSeries:
    if isinstance(data, OhlcvSeries):
        return data
    return _as_frame(data)[column]
