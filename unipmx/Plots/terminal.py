"""ASCII terminal charts."""

from __future__ import annotations

from rich.text import Text

from unipmx.Display.utils import console, fmt_ts, print_block, subtitle
from unipmx.models import OhlcvSeries

_BLOCKS = "▁▂▃▄▅▆▇█"


def _resample(values: list[float], width: int) -> list[float]:
    if width <= 0:
        return []
    if len(values) <= width:
        return values
    step = len(values) / width
    return [values[int(i * step + step / 2)] for i in range(width)]


def _sparkline(values: list[float], width: int) -> str:
    sampled = _resample(values, width)
    if not sampled:
        return ""
    lo, hi = min(sampled), max(sampled)
    if hi == lo:
        return _BLOCKS[4] * len(sampled)
    span = hi - lo
    return "".join(_BLOCKS[min(7, int((v - lo) / span * 7))] for v in sampled)


def _vertical_chart(values: list[float], *, width: int, height: int) -> Text:
    sampled = _resample(values, width)
    if not sampled:
        return Text("")

    lo, hi = min(sampled), max(sampled)
    if hi == lo:
        rows = [" " * width] * (height - 1) + ["█" * width]
    else:
        span = hi - lo
        grid = [[" "] * width for _ in range(height)]
        for x, value in enumerate(sampled):
            row = height - 1 - int((value - lo) / span * (height - 1))
            grid[row][x] = "█"
        rows = ["".join(row) for row in grid]

    lines = Text()
    for i, row in enumerate(rows):
        if i == 0 and hi != lo:
            lines.append(f"{_fmt_value(hi, values):>7} │ ", style="dim")
        elif i == len(rows) - 1:
            lines.append(f"{_fmt_value(lo, values):>7} │ ", style="dim")
        else:
            lines.append("        │ ", style="dim")
        lines.append(row, style="cyan")
        lines.append("\n")
    lines.append("        └" + "─" * width + "\n", style="dim")
    return lines


def _fmt_value(value: float, all_values: list[float]) -> str:
    is_price = all(isinstance(v, float) and 0 <= v <= 1 for v in all_values if v is not None)
    if is_price:
        return f"{value * 100:.0f}%"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:.0f}"


def _series_stats(series: OhlcvSeries) -> str:
    values = series.values
    lo, hi = min(values), max(values)
    latest = values[-1]
    is_price = series.name.lower() in ("open", "high", "low", "close")
    if is_price:
        return (
            f"[dim]{len(values)} pts ·[/dim] "
            f"[red]low {lo * 100:.1f}%[/red]  "
            f"[green]high {hi * 100:.1f}%[/green]  "
            f"[bold]last {latest * 100:.1f}%[/bold]"
        )
    return (
        f"[dim]{len(values)} pts ·[/dim] "
        f"[red]low {_fmt_value(lo, values)}[/red]  "
        f"[green]high {_fmt_value(hi, values)}[/green]  "
        f"[bold]last {_fmt_value(latest, values)}[/bold]"
    )


def plotTerminal(series: OhlcvSeries, *, title: str | None = None) -> None:
    """Sparkline + block chart in the terminal."""
    name = title or series.name.title()
    values = series.values

    if not values:
        print_block(name, subtitle("[italic]No data.[/italic]"), border_style="bright_cyan")
        return

    width = min(64, max(console.width - 12, 24), len(values))
    parts = [
        subtitle(_series_stats(series)),
        Text(_sparkline(values, width), style="cyan"),
        _vertical_chart(values, width=width, height=8),
    ]
    times = [t for t in series.timestamps if t]
    if times:
        parts.append(subtitle(f"[dim]{fmt_ts(int(times[0]))} → {fmt_ts(int(times[-1]))}[/dim]"))
    print_block(name, *parts, border_style="bright_cyan")
