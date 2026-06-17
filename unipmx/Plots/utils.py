"""Shared helpers for Plots module."""

from __future__ import annotations

import json
import tempfile
import webbrowser
from pathlib import Path
from uuid import uuid4

# TradingView dark theme
TV_THEME = {
    "bg": "#131722",
    "text": "#d1d4dc",
    "grid": "#1e222d",
    "border": "#2a2e39",
    "up": "#26a69a",
    "down": "#ef5350",
    "line": "#2962FF",
    "line_fill_top": "rgba(41, 98, 255, 0.28)",
    "line_fill_bottom": "rgba(41, 98, 255, 0.02)",
}

LIGHTWEIGHT_CHARTS_CDN = (
    "https://unpkg.com/lightweight-charts@4.2.0/dist/lightweight-charts.standalone.production.js"
)


def time_sec(ms: int | None) -> int | None:
    return int(ms // 1000) if ms else None


def openHtml(html: str) -> None:
    path = Path(tempfile.gettempdir()) / f"pm-chart-{uuid4().hex}.html"
    path.write_text(html, encoding="utf-8")
    webbrowser.open(path.as_uri())


def chartPage(title: str, chart_js: str) -> str:
    t = TV_THEME
    safe_title = json.dumps(title)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>{title}</title>
  <script src="{LIGHTWEIGHT_CHARTS_CDN}"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: {t["bg"]}; font-family: -apple-system, BlinkMacSystemFont, "Trebuchet MS", sans-serif; }}
    #header {{
      padding: 12px 16px 8px;
      color: {t["text"]};
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid {t["border"]};
    }}
    #chart {{ width: 100vw; height: calc(100vh - 42px); }}
  </style>
</head>
<body>
  <div id="header">{title}</div>
  <div id="chart"></div>
  <script>
    const container = document.getElementById('chart');
    const chart = LightweightCharts.createChart(container, {{
      layout: {{
        background: {{ type: 'solid', color: '{t["bg"]}' }},
        textColor: '{t["text"]}',
        fontSize: 12,
        fontFamily: '-apple-system, BlinkMacSystemFont, "Trebuchet MS", sans-serif',
      }},
      grid: {{
        vertLines: {{ color: '{t["grid"]}' }},
        horzLines: {{ color: '{t["grid"]}' }},
      }},
      crosshair: {{ mode: LightweightCharts.CrosshairMode.Normal }},
      rightPriceScale: {{ borderColor: '{t["border"]}' }},
      timeScale: {{
        borderColor: '{t["border"]}',
        timeVisible: true,
        secondsVisible: false,
      }},
    }});
    new ResizeObserver(() => {{
      chart.applyOptions({{ width: container.clientWidth, height: container.clientHeight }});
    }}).observe(container);
    {chart_js}
  </script>
</body>
</html>"""
