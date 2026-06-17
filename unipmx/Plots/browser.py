"""TradingView-style browser charts (lightweight-charts)."""

from __future__ import annotations

import json

from unipmx.models import OhlcvCandles, OhlcvFrame, OhlcvSeries

from .utils import TV_THEME, chartPage, openHtml, time_sec


def _is_price(series: OhlcvSeries) -> bool:
    return series.name.lower() in ("open", "high", "low", "close")


def plotSeries(series: OhlcvSeries, *, title: str | None = None) -> None:
    """Area line or volume histogram in the browser."""
    if not series.values:
        raise ValueError("No data to plot")

    label = title or series.name.title()
    name = series.name.lower()
    scale = 100.0 if _is_price(series) else 1.0
    t = TV_THEME

    if name == "volume":
        points = []
        for i, v in enumerate(series.values):
            ts = time_sec(series.timestamps[i] if i < len(series.timestamps) else None)
            if ts is None:
                continue
            points.append({"time": ts, "value": v, "color": t["up"]})
        js = f"""
    const series = chart.addHistogramSeries({{
      priceFormat: {{ type: 'volume' }},
      priceScaleId: '',
    }});
    series.setData({json.dumps(points)});
    chart.timeScale().fitContent();
"""
    else:
        points = []
        for i, v in enumerate(series.values):
            ts = time_sec(series.timestamps[i] if i < len(series.timestamps) else None)
            if ts is None:
                continue
            points.append({"time": ts, "value": round(v * scale, 4)})
        js = f"""
    const series = chart.addAreaSeries({{
      lineColor: '{t["line"]}',
      topColor: '{t["line_fill_top"]}',
      bottomColor: '{t["line_fill_bottom"]}',
      lineWidth: 2,
      priceFormat: {{ type: 'price', precision: 2, minMove: 0.01 }},
    }});
    series.setData({json.dumps(points)});
    chart.timeScale().fitContent();
"""
    openHtml(chartPage(label, js))


def plotCandles(
    data: OhlcvFrame | OhlcvCandles,
    *,
    title: str | None = None,
) -> None:
    """Candlestick chart with bodies, wicks (doji/hammer/etc.), and volume."""
    candles = data.candles
    if not candles:
        raise ValueError("No candles to plot")

    label = title or "OHLCV"
    t = TV_THEME
    ohlc = []
    volume = []
    for c in candles:
        ts = time_sec(c.timestamp)
        if ts is None:
            continue
        o = round(c.open * 100, 4)
        h = round(c.high * 100, 4)
        lo = round(c.low * 100, 4)
        cl = round(c.close * 100, 4)
        ohlc.append({"time": ts, "open": o, "high": h, "low": lo, "close": cl})
        vol = c.volume or 0
        color = "rgba(38, 166, 154, 0.5)" if cl >= o else "rgba(239, 83, 80, 0.5)"
        volume.append({"time": ts, "value": vol, "color": color})

    vol_js = ""
    if any(v["value"] for v in volume):
        vol_js = f"""
    const volumeSeries = chart.addHistogramSeries({{
      priceFormat: {{ type: 'volume' }},
      priceScaleId: '',
    }});
    volumeSeries.priceScale().applyOptions({{
      scaleMargins: {{ top: 0.82, bottom: 0 }},
    }});
    volumeSeries.setData({json.dumps(volume)});
    chart.priceScale('right').applyOptions({{
      scaleMargins: {{ top: 0.05, bottom: 0.22 }},
    }});
"""

    js = f"""
    const candleSeries = chart.addCandlestickSeries({{
      upColor: '{t["up"]}',
      downColor: '{t["down"]}',
      borderUpColor: '{t["up"]}',
      borderDownColor: '{t["down"]}',
      wickUpColor: '{t["up"]}',
      wickDownColor: '{t["down"]}',
      priceFormat: {{ type: 'price', precision: 2, minMove: 0.01 }},
    }});
    candleSeries.setData({json.dumps(ohlc)});
    {vol_js}
    chart.timeScale().fitContent();
"""
    openHtml(chartPage(label, js))
