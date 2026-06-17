"""Rich formatting helpers and per-type renderers."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Callable, TypeVar

from rich.columns import Columns
from rich.console import Console, Group
from rich.panel import Panel
from rich.status import Status
from rich.table import Table
from rich.style import Style
from rich.text import Text

_spinner_depth = 0

from pmxt.models import (
    Balance,
    Order,
    OrderBook,
    Position,
    PriceCandle,
    SubscribedAddressSnapshot,
    Trade,
    UnifiedEvent,
    UnifiedMarket,
    UnifiedSeries,
    UserTrade,
)

from unipmx.models import (
    Comment,
    EventResult,
    Holder,
    MarketPosition,
    MarketRules,
    MarketStats,
    MarketResult,
    PricePoint,
    Resolution,
    SearchResults,
    SeriesResult,
)

console = Console()

EXCHANGE_STYLES: dict[str, str] = {
    "Polymarket": "cyan",
    "Kalshi": "magenta",
    "Limitless": "yellow",
    "Myriad": "green",
    "Probable": "blue",
    "Smarkets": "red",
}


def get_console() -> Console:
    return console


@contextmanager
def loading(message: str = "Loading…"):
    """Animated dot spinner — skips nesting when already active."""
    global _spinner_depth
    if _spinner_depth > 0:
        yield _NestedStatus()
        return

    _spinner_depth += 1
    try:
        with console.status(
            f"[dim]{message}[/dim]",
            spinner="dots",
            spinner_style="cyan",
        ) as status:
            yield status
    finally:
        _spinner_depth -= 1


class _NestedStatus:
    def update(self, *_args, **_kwargs) -> None:
        pass


T = TypeVar("T")


def withSpinner(message: str, fn: Callable[[], T]) -> T:
    with loading(message):
        return fn()


def exchange_border(name: str) -> str:
    return EXCHANGE_STYLES.get(name, "bright_blue")


def fmt_pct(value: float | None) -> str:
    return f"{value * 100:.1f}%" if value is not None else "—"


def fmt_volume(value: float | None) -> str:
    return f"${value:,.0f}" if value else "—"


def fmt_cents(value: float) -> str:
    return f"{value * 100:.2f}¢"


def fmt_ts(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000).strftime("%Y-%m-%d %H:%M")


def truncate(text: str, max_len: int = 55) -> str:
    text = " ".join(str(text).split())
    return text if len(text) <= max_len else text[: max_len - 1] + "…"


def link_cell(label: str, url: str | None, *, max_len: int = 55) -> Text:
    """Terminal hyperlink cell — Ctrl/Cmd+click opens url in supported terminals."""
    cell = Text(truncate(label, max_len))
    if url:
        cell.stylize(Style(link=url, color="cyan", underline=True))
    return cell


def link_heading(label: str, url: str | None, *, suffix: str = "") -> Text:
    from rich.markup import escape

    head = escape(truncate(label, 80))
    if url:
        line = Text.from_markup(f"[bold][link={url}]{head}[/link][/bold]")
    else:
        line = Text.from_markup(f"[bold]{head}[/bold]")
    if suffix:
        line.append_text(Text.from_markup(suffix))
    return line


def to_yes_no_prices(outcomes) -> tuple[float | None, float | None]:
    if not outcomes:
        return None, None
    yes_price = no_price = None
    for o in outcomes:
        low = o.label.lower().strip()
        if low in ("yes", "y"):
            yes_price = o.price
        elif low in ("no", "n"):
            no_price = o.price
    if yes_price is not None or no_price is not None:
        return yes_price, no_price
    if len(outcomes) == 2:
        a, b = outcomes[0], outcomes[1]
        if b.label.lower().startswith("not "):
            return a.price, b.price
        if a.label.lower().startswith("not "):
            return b.price, a.price
        return a.price, b.price
    return outcomes[0].price, outcomes[1].price if len(outcomes) > 1 else None


def market_question(event_title: str | None, market_title: str) -> str:
    if event_title and market_title.startswith(event_title):
        rest = market_title[len(event_title) :].lstrip(" -–—:")
        if rest:
            return rest
    if " - " in market_title:
        return market_title.split(" - ", 1)[1]
    return market_title


def subtitle(text: str) -> Text:
    return Text.from_markup(text)


def search_meta(*, sort: str | None = None, status: str | None = None) -> str:
    parts = [p for p in (status, sort) if p]
    return f" · {' · '.join(parts)}" if parts else ""


def build_panel(title: str, *parts, border_style: str = "bright_blue") -> Panel:
    return Panel(
        Group(*parts),
        title=f"[bold]{title}[/bold]",
        border_style=border_style,
        padding=(0, 1),
    )


def show_panel(panel: Panel) -> None:
    """Print exactly one bordered panel — called once per display()."""
    console.print(panel)
    console.print()


def print_block(title: str, *parts, border_style: str = "bright_blue") -> None:
    show_panel(build_panel(title, *parts, border_style=border_style))


def make_table(*, embedded: bool = True, show_header: bool = True) -> Table:
    from rich import box

    return Table(
        box=box.SIMPLE if embedded else box.ROUNDED,
        show_header=show_header,
        header_style="bold bright_white",
        border_style="dim" if embedded else "bright_black",
        expand=True,
        pad_edge=False,
    )


def _markets_table(markets: list[UnifiedMarket]) -> Table:
    table = make_table()
    table.add_column("#", width=3, justify="right", style="dim", no_wrap=True)
    table.add_column("Market", ratio=1, no_wrap=True, overflow="ellipsis")
    table.add_column("Yes", justify="right", style="green", no_wrap=True)
    table.add_column("No", justify="right", style="red", no_wrap=True)
    for i, m in enumerate(markets, 1):
        yes, no = to_yes_no_prices(m.outcomes)
        table.add_row(str(i), link_cell(m.title, m.url), fmt_pct(yes), fmt_pct(no))
    return table


def render_markets(
    data: UnifiedMarket | list[UnifiedMarket],
    *,
    title: str = "Markets",
    exchange: str | None = None,
    query: str | None = None,
    limit: int | None = None,
) -> Panel:
    markets = [data] if isinstance(data, UnifiedMarket) else list(data)
    if not markets:
        return build_panel(title, subtitle("[italic]No markets.[/italic]"), border_style="yellow")
    parts: list = []
    if query:
        parts.append(subtitle(f"[dim]Search:[/dim] [italic]'{query}'[/italic]" + (f"  · top {limit}" if limit else "")))
    parts.append(_markets_table(markets))
    return build_panel(title, *parts, border_style=exchange_border(exchange or "Polymarket"))


def render_events(
    data: UnifiedEvent | list[UnifiedEvent],
    *,
    title: str = "Events",
    exchange: str | None = None,
    query: str | None = None,
    show_markets: bool = True,
) -> Panel:
    events = [data] if isinstance(data, UnifiedEvent) else list(data)
    if not events:
        return build_panel(title, subtitle("[italic]No events.[/italic]"), border_style="yellow")
    border = exchange_border(exchange or "Polymarket")
    parts: list = []
    if query:
        parts.append(subtitle(f"[dim]Search:[/dim] [italic]'{query}'[/italic]"))
    for i, event in enumerate(events, 1):
        if i > 1:
            parts.append(subtitle(""))
        meta = f"{len(event.markets)} markets"
        if event.volume:
            meta += f"  · vol {fmt_volume(event.volume)}"
        parts.append(link_heading(event.title, event.url, suffix=f"  [dim]({meta})[/dim]"))
        if show_markets and event.markets:
            table = make_table()
            table.add_column("Market", ratio=1, no_wrap=True, overflow="ellipsis")
            table.add_column("Yes", justify="right", style="green", no_wrap=True)
            table.add_column("No", justify="right", style="red", no_wrap=True)
            for market in event.markets[:8]:
                yes, no = to_yes_no_prices(market.outcomes)
                q = market_question(event.title, market.title)
                table.add_row(link_cell(q, market.url), fmt_pct(yes), fmt_pct(no))
            if len(event.markets) > 8:
                table.add_row(Text(f"… +{len(event.markets) - 8} more", style="dim"), "", "")
            parts.append(table)
    return build_panel(title, *parts, border_style=border)


def render_series(
    data: UnifiedSeries | list[UnifiedSeries],
    *,
    title: str = "Series",
    exchange: str | None = None,
    query: str | None = None,
    show_events: bool = True,
    show_markets: bool = True,
) -> Panel:
    items = [data] if isinstance(data, UnifiedSeries) else list(data)
    if not items:
        return build_panel(title, subtitle("[italic]No series.[/italic]"), border_style="yellow")
    border = exchange_border(exchange or "Polymarket")
    parts: list = []
    if query:
        parts.append(subtitle(f"[dim]Search:[/dim] [italic]'{query}'[/italic]"))
    for i, series in enumerate(items, 1):
        if i > 1:
            parts.append(subtitle(""))
        recur = f"  [dim]· {series.recurrence}[/dim]" if series.recurrence else ""
        parts.append(link_heading(series.title, series.url, suffix=recur))
        if not show_events or not series.events:
            continue
        for j, event in enumerate(series.events):
            if j > 0:
                parts.append(subtitle(""))
            meta = f"{len(event.markets)} markets"
            if event.volume:
                meta += f"  · vol {fmt_volume(event.volume)}"
            parts.append(
                link_heading(event.title, event.url, suffix=f"  [dim]({meta})[/dim]")
            )
            if show_markets and event.markets:
                table = make_table()
                table.add_column("Market", ratio=1, no_wrap=True, overflow="ellipsis")
                table.add_column("Yes", justify="right", style="green", no_wrap=True)
                table.add_column("No", justify="right", style="red", no_wrap=True)
                for market in event.markets[:8]:
                    yes, no = to_yes_no_prices(market.outcomes)
                    q = market_question(event.title, market.title)
                    table.add_row(link_cell(q, market.url), fmt_pct(yes), fmt_pct(no))
                if len(event.markets) > 8:
                    table.add_row(Text(f"… +{len(event.markets) - 8} more", style="dim"), "", "")
                parts.append(table)
    return build_panel(title, *parts, border_style=border)


def render_search_events(results: list[EventResult], *, query: str, sort: str | None = None, status: str | None = None) -> Panel:
    title = f"Events · '{query}'"
    if not results:
        return build_panel(title, subtitle("[italic]No results.[/italic]"), border_style="cyan")
    by_ex: dict[str, list[EventResult]] = {}
    for r in results:
        by_ex.setdefault(r.exchange, []).append(r)
    parts: list = []
    for i, (exchange, items) in enumerate(by_ex.items()):
        if i > 0:
            parts.append(subtitle(""))
        table = make_table()
        table.add_column("Event", ratio=1, no_wrap=True, overflow="ellipsis")
        table.add_column("Markets", justify="right", no_wrap=True)
        table.add_column("Volume", justify="right", style="dim", no_wrap=True)
        for item in items:
            table.add_row(link_cell(item.title, item.url), str(item.market_count), fmt_volume(item.volume))
        parts.append(subtitle(f"[bold]{exchange}[/bold]  [dim]· {len(items)} events{search_meta(sort=sort, status=status)}[/dim]"))
        parts.append(table)
    return build_panel(title, *parts, border_style="cyan")


def render_search_series(results: list[SeriesResult], *, query: str, sort: str | None = None) -> Panel:
    title = f"Series · '{query}'"
    if not results:
        return build_panel(title, subtitle("[italic]No results.[/italic]"), border_style="cyan")
    by_ex: dict[str, list[SeriesResult]] = {}
    for r in results:
        by_ex.setdefault(r.exchange, []).append(r)
    parts: list = []
    for i, (exchange, items) in enumerate(by_ex.items()):
        if i > 0:
            parts.append(subtitle(""))
        table = make_table()
        table.add_column("Series", ratio=1, no_wrap=True, overflow="ellipsis")
        table.add_column("Recurrence", no_wrap=True)
        for item in items:
            table.add_row(link_cell(item.title, item.url), item.recurrence or "—")
        parts.append(subtitle(f"[bold]{exchange}[/bold]  [dim]· {len(items)} series{(' · ' + sort) if sort else ''}[/dim]"))
        parts.append(table)
    return build_panel(title, *parts, border_style="cyan")


def render_search_results(results: list[MarketResult], *, query: str, sort: str | None = None, status: str | None = None) -> Panel:
    title = f"Search · '{query}'"
    if not results:
        return build_panel(title, subtitle("[italic]No results.[/italic]"), border_style="cyan")
    by_ex: dict[str, list[MarketResult]] = {}
    for r in results:
        by_ex.setdefault(r.exchange, []).append(r)
    parts: list = []
    for i, (exchange, items) in enumerate(by_ex.items()):
        if i > 0:
            parts.append(subtitle(""))
        table = make_table()
        table.add_column("Market", ratio=1, no_wrap=True, overflow="ellipsis")
        table.add_column("Yes", justify="right", style="green", no_wrap=True)
        table.add_column("No", justify="right", style="red", no_wrap=True)
        table.add_column("Volume", justify="right", style="dim", no_wrap=True)
        for item in items:
            table.add_row(
                link_cell(item.title, item.url),
                fmt_pct(item.yes_price),
                fmt_pct(item.no_price),
                fmt_volume(item.volume),
            )
        parts.append(subtitle(f"[bold]{exchange}[/bold]  [dim]· {len(items)} markets{search_meta(sort=sort, status=status)}[/dim]"))
        parts.append(table)
    return build_panel(title, *parts, border_style="cyan")


def _order_book_parts(
    book: OrderBook,
    *,
    market_title: str = "",
    market_url: str | None = None,
    price_line=None,
    query: str | None = None,
) -> list:
    asks = make_table()
    asks.add_column("Ask", justify="right", style="red", no_wrap=True)
    asks.add_column("Size", justify="right", no_wrap=True)
    bids = make_table()
    bids.add_column("Bid", justify="right", style="green", no_wrap=True)
    bids.add_column("Size", justify="right", no_wrap=True)
    for a in book.asks[:10]:
        asks.add_row(fmt_cents(a.price), f"{a.size:.0f}")
    for b in book.bids[:10]:
        bids.add_row(fmt_cents(b.price), f"{b.size:.0f}")

    parts: list = []
    if query:
        parts.append(subtitle(f"[dim]Query:[/dim] [italic]'{query}'[/italic]"))
    if price_line:
        parts.append(price_line)
    elif market_title:
        parts.append(link_heading(market_title, market_url))
    parts.append(Columns([asks, bids], equal=True, expand=True))
    if book.asks and book.bids:
        spread = (book.asks[0].price - book.bids[0].price) * 100
        parts.append(subtitle(f"[dim]Spread:[/dim] [yellow]{spread:.2f}¢[/yellow]"))
    return parts


def render_order_book(
    data: OrderBook | tuple,
    *,
    title: str = "Order Book",
    exchange: str | None = None,
    query: str | None = None,
) -> Panel:
    market_title = ""
    market_url = None
    if isinstance(data, tuple) and len(data) == 3:
        market, outcome, book = data
        market_title = market.title
        market_url = market.url
        yes, _ = to_yes_no_prices(market.outcomes)
        price_line = link_heading(market.title, market.url, suffix=f"\n[dim]Yes[/dim] [green]{fmt_pct(yes)}[/green]")
        data = book
    else:
        book = data
        price_line = None

    parts = _order_book_parts(
        book, market_title=market_title, market_url=market_url, price_line=price_line, query=query
    )
    return build_panel(title, *parts, border_style=exchange_border(exchange or "Polymarket"))


def render_order_books(
    books: dict[str, OrderBook],
    *,
    title: str = "Order Books",
    exchange: str | None = None,
) -> Panel:
    parts: list = []
    for i, (oid, book) in enumerate(list(books.items())[:3]):
        if i > 0:
            parts.append(subtitle(""))
        parts.append(subtitle(f"[bold]{oid[:16]}…[/bold]"))
        parts.extend(_order_book_parts(book))
    if not parts:
        parts.append(subtitle("[italic]No order books.[/italic]"))
    return build_panel(title, *parts, border_style=exchange_border(exchange or "Polymarket"))


def _trades_table(trades: list[Trade | UserTrade]) -> Table:
    table = make_table()
    table.add_column("Time", no_wrap=True)
    table.add_column("Side", no_wrap=True)
    table.add_column("Price", justify="right", style="green", no_wrap=True)
    table.add_column("Size", justify="right", no_wrap=True)
    table.add_column("Market", ratio=1, no_wrap=True, overflow="ellipsis")
    for t in trades[:50]:
        market = getattr(t, "market_id", "") or ""
        table.add_row(fmt_ts(t.timestamp), t.side, fmt_pct(t.price), f"{t.amount:.2f}", truncate(str(market), 30))
    return table


def render_trades(trades: list[Trade | UserTrade], *, title: str = "Trades") -> Panel:
    if not trades:
        return build_panel(title, subtitle("[italic]No trades.[/italic]"), border_style="yellow")
    return build_panel(title, _trades_table(trades), border_style="bright_green")


def _positions_table(positions: list[Position]) -> Table:
    table = make_table()
    table.add_column("Outcome", ratio=1, no_wrap=True, overflow="ellipsis")
    table.add_column("Size", justify="right", no_wrap=True)
    table.add_column("Entry", justify="right", no_wrap=True)
    table.add_column("Mark", justify="right", style="green", no_wrap=True)
    table.add_column("PnL", justify="right", no_wrap=True)
    for p in positions:
        pnl = f"{p.unrealized_pnl:+.2f}" if p.unrealized_pnl is not None else "—"
        table.add_row(
            truncate(p.outcome_label or p.outcome_id, 40),
            f"{p.size:.2f}",
            fmt_pct(p.entry_price) if p.entry_price else "—",
            fmt_pct(p.current_price) if p.current_price else "—",
            pnl,
        )
    return table


def render_positions(positions: list[Position], *, title: str = "Positions", address: str | None = None) -> Panel:
    if not positions:
        return build_panel(title, subtitle("[italic]No open positions.[/italic]"), border_style="yellow")
    parts: list = []
    if address:
        parts.append(subtitle(f"[dim]Wallet:[/dim] {address[:10]}…{address[-6:]}"))
    parts.append(_positions_table(positions))
    return build_panel(title, *parts, border_style="bright_magenta")


def _balances_table(balances: list[Balance]) -> Table:
    table = make_table()
    table.add_column("Asset", no_wrap=True)
    table.add_column("Available", justify="right", no_wrap=True)
    table.add_column("Locked", justify="right", no_wrap=True)
    table.add_column("Total", justify="right", style="green", no_wrap=True)
    for b in balances:
        table.add_row(b.currency, f"{b.available:.2f}", f"{b.locked:.2f}", f"{b.total:.2f}")
    return table


def render_balances(balances: list[Balance], *, title: str = "Balance", address: str | None = None) -> Panel:
    if not balances:
        return build_panel(title, subtitle("[italic]No balance data.[/italic]"), border_style="yellow")
    parts: list = []
    if address:
        parts.append(subtitle(f"[dim]Wallet:[/dim] {address[:10]}…{address[-6:]}"))
    parts.append(_balances_table(balances))
    return build_panel(title, *parts, border_style="bright_blue")


def render_orders(orders: list[Order], *, title: str = "Orders") -> Panel:
    if not orders:
        return build_panel(title, subtitle("[italic]No orders.[/italic]"), border_style="yellow")
    table = make_table()
    table.add_column("ID", no_wrap=True, overflow="ellipsis")
    table.add_column("Side", no_wrap=True)
    table.add_column("Type", no_wrap=True)
    table.add_column("Price", justify="right", no_wrap=True)
    table.add_column("Amount", justify="right", no_wrap=True)
    table.add_column("Status", no_wrap=True)
    for o in orders[:50]:
        price = getattr(o, "price", None)
        table.add_row(
            truncate(o.id, 12),
            o.side,
            o.type,
            fmt_pct(price) if price is not None else "—",
            f"{o.amount:.2f}",
            o.status or "—",
        )
    return build_panel(title, table, border_style="bright_yellow")


def render_ohlcv(candles: list[PriceCandle], *, title: str = "OHLCV") -> Panel:
    if not candles:
        return build_panel(title, subtitle("[italic]No candles.[/italic]"), border_style="yellow")
    table = make_table()
    table.add_column("Time", no_wrap=True)
    table.add_column("Open", justify="right", no_wrap=True)
    table.add_column("High", justify="right", no_wrap=True)
    table.add_column("Low", justify="right", no_wrap=True)
    table.add_column("Close", justify="right", style="green", no_wrap=True)
    table.add_column("Vol", justify="right", style="dim", no_wrap=True)
    for c in candles[-30:]:
        ts = fmt_ts(int(c.timestamp)) if c.timestamp else "—"
        table.add_row(ts, fmt_pct(c.open), fmt_pct(c.high), fmt_pct(c.low), fmt_pct(c.close), f"{(c.volume or 0):.0f}")
    return build_panel(title, table, border_style="bright_cyan")


def render_user_activity(activity, *, title: str = "User Activity") -> Panel:
    addr = activity.address
    parts: list = [subtitle(f"[dim]Wallet:[/dim] [cyan]{addr}[/cyan]")]
    parts.append(subtitle("[bold]Balances[/bold]"))
    if activity.balances:
        parts.append(_balances_table(activity.balances))
    else:
        parts.append(subtitle("[italic]No balance data.[/italic]"))
    parts.append(subtitle("[bold]Positions[/bold]"))
    if activity.positions:
        parts.append(_positions_table(activity.positions))
    else:
        parts.append(subtitle("[italic]No open positions.[/italic]"))
    parts.append(subtitle("[bold]Recent Trades[/bold]"))
    if activity.trades:
        parts.append(_trades_table(activity.trades))
    else:
        parts.append(subtitle("[italic]No trades.[/italic]"))
    return build_panel(title, *parts, border_style="bright_magenta")


def render_address_snapshot(snap: SubscribedAddressSnapshot, *, title: str = "Wallet Feed") -> Panel:
    parts: list = [subtitle(f"[dim]Wallet:[/dim] [cyan]{snap.address}[/cyan]  [dim]· {fmt_ts(snap.timestamp)}[/dim]")]
    if snap.balances:
        parts.append(subtitle("[bold]Balances[/bold]"))
        parts.append(_balances_table(snap.balances))
    if snap.positions:
        parts.append(subtitle("[bold]Positions[/bold]"))
        parts.append(_positions_table(snap.positions))
    if snap.trades:
        parts.append(subtitle("[bold]Trades[/bold]"))
        parts.append(_trades_table(snap.trades))
    if len(parts) == 1:
        parts.append(subtitle("[italic]No updates yet.[/italic]"))
    return build_panel(title, *parts, border_style="bright_magenta")


def render_compare(grouped: dict[str, list[UnifiedMarket]], *, query: str) -> Panel:
    parts: list = [subtitle(f"[dim]Query:[/dim] [italic]'{query}'[/italic]")]
    for i, (exchange, markets) in enumerate(grouped.items()):
        if i > 0:
            parts.append(subtitle(""))
        parts.append(subtitle(f"[bold]{exchange}[/bold]  [dim]· {len(markets)} markets[/dim]"))
        parts.append(_markets_table(markets))
    return build_panel(f"Compare · '{query}'", *parts, border_style="cyan")


def render_generic(data: Any, *, title: str = "Data") -> Panel:
    from rich.json import JSON
    from rich.pretty import Pretty

    try:
        if hasattr(data, "__dict__"):
            return build_panel(title, Pretty(data), border_style="dim")
        return build_panel(title, JSON.from_data(data), border_style="dim")
    except Exception:
        return build_panel(title, subtitle(str(data)[:2000]), border_style="dim")


def fmt_comment_time(created_at: str | None) -> str:
    if not created_at:
        return ""
    try:
        from datetime import datetime, timezone

        ts = created_at.replace("Z", "+00:00")
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - dt
        if delta.days == 0:
            hours = int(delta.total_seconds() // 3600)
            if hours < 1:
                mins = max(1, int(delta.total_seconds() // 60))
                return f"{mins}m ago"
            return f"{hours}h ago"
        if delta.days < 7:
            return f"{delta.days}d ago"
        return dt.strftime("%b %d %Y")
    except (ValueError, TypeError):
        return created_at[:16] if created_at else ""


def _comment_depth(comment: Comment, by_id: dict[str, Comment]) -> int:
    depth = 0
    seen: set[str] = set()
    current = comment
    while current.parent_comment_id and current.parent_comment_id not in seen:
        seen.add(current.parent_comment_id)
        parent = by_id.get(current.parent_comment_id)
        if not parent:
            break
        depth += 1
        current = parent
    return depth


def _resolve_reply_to(comment: Comment, by_id: dict[str, Comment]) -> str | None:
    if comment.parent_comment_id:
        parent = by_id.get(comment.parent_comment_id)
        if parent and parent.author:
            return parent.author
    body = comment.body.lstrip()
    if body.startswith("@"):
        mention = body[1:].split()[0].rstrip(".,:;!?")
        if mention:
            return mention
    return None


def _comment_body_text(body: str, *, indent: str = "") -> Text:
    import re

    line = Text(indent)
    for i, part in enumerate(re.split(r"(@\w[\w.-]*)", body)):
        if i % 2 == 1:
            line.append(part, style="cyan bold")
        else:
            line.append(part)
    return line


def render_comments(comments: list[Comment], *, title: str = "Comments") -> Panel:
    if not comments:
        return build_panel(title, subtitle("[italic]No comments.[/italic]"), border_style="bright_blue")

    by_id = {c.id: c for c in comments}
    for c in comments:
        c.reply_to = _resolve_reply_to(c, by_id)

    ordered = sorted(comments, key=lambda c: c.created_at or "")

    parts: list = []
    for c in ordered[:80]:
        depth = _comment_depth(c, by_id)
        pad = "  " * depth
        is_reply = depth > 0 or c.parent_comment_id

        if is_reply and c.reply_to:
            parts.append(Text.from_markup(f"{pad}[dim]↳ replying to [/dim][cyan]@{c.reply_to}[/cyan]"))
        elif is_reply:
            parts.append(Text.from_markup(f"{pad}[dim]↳ reply[/dim]"))

        meta = fmt_comment_time(c.created_at)
        header = f"{pad}[bold]{c.author or 'anon'}[/bold]"
        if meta:
            header += f"  [dim]{meta}[/dim]"
        if c.reaction_count:
            header += f"  [dim]♥ {c.reaction_count}[/dim]"
        parts.append(Text.from_markup(header))
        parts.append(_comment_body_text(c.body, indent=pad))
        parts.append(Text(""))

    return build_panel(title, *parts, border_style="bright_blue")


def render_holders(holders: list[Holder], *, title: str = "Top Holders") -> Panel:
    table = make_table()
    table.add_column("Name", no_wrap=True)
    table.add_column("Outcome", no_wrap=True)
    table.add_column("Amount", justify="right", no_wrap=True)
    table.add_column("Address", no_wrap=True, style="dim")
    for h in holders[:30]:
        table.add_row(h.name or "—", h.outcome or "—", f"{h.amount:,.2f}", truncate(h.address, 14))
    return build_panel(title, table, border_style="bright_green")


def render_market_stats(stats: MarketStats, *, title: str = "Market Stats") -> Panel:
    table = make_table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value", justify="right")
    for label, val in [
        ("Volume", stats.volume),
        ("Liquidity", stats.liquidity),
        ("Open Interest", stats.open_interest),
        ("Unique Traders", stats.unique_traders),
    ]:
        table.add_row(label, f"{val:,.2f}" if isinstance(val, float) else (str(val) if val is not None else "—"))
    return build_panel(title or f"Stats · {stats.market_id}", table, border_style="bright_cyan")


def render_resolution(res: Resolution, *, title: str = "Resolution") -> Panel:
    table = make_table(show_header=False)
    table.add_column("Field", style="dim")
    table.add_column("Value")
    for label, val in [
        ("Status", res.status),
        ("Outcome", res.outcome),
        ("Resolved By", res.resolved_by),
        ("Resolved At", res.resolved_at),
        ("Source", res.resolution_source),
    ]:
        table.add_row(label, str(val) if val is not None else "—")
    return build_panel(title or f"Resolution · {res.market_id}", table, border_style="bright_yellow")


def render_market_rules(rules: MarketRules, *, title: str = "Market Rules") -> Panel:
    parts: list = []
    if rules.description:
        parts.append(subtitle(truncate(rules.description, 300)))
    if rules.resolution_source:
        parts.append(subtitle(f"[dim]Resolution source:[/dim] {rules.resolution_source}"))
    if rules.criteria:
        parts.append(subtitle(f"[dim]Criteria:[/dim] {rules.criteria}"))
    if not parts:
        parts.append(subtitle("—"))
    return build_panel(title or f"Rules · {rules.market_id}", *parts, border_style="bright_white")


def render_price_points(points: list[PricePoint], *, title: str = "Price History") -> Panel:
    if not points:
        return build_panel(title, subtitle("[italic]No price data.[/italic]"), border_style="yellow")
    table = make_table()
    table.add_column("Time", no_wrap=True)
    table.add_column("YES", justify="right", no_wrap=True)
    table.add_column("NO", justify="right", no_wrap=True)
    for p in points[-30:]:
        ts = fmt_ts(p.timestamp) if p.timestamp else "—"
        table.add_row(ts, fmt_pct(p.yes_price), fmt_pct(p.no_price))
    return build_panel(title, table, border_style="bright_cyan")


def render_market_positions(positions: list[MarketPosition], *, title: str = "Market Positions") -> Panel:
    table = make_table()
    table.add_column("Address", no_wrap=True, style="dim")
    table.add_column("Outcome", no_wrap=True)
    table.add_column("Size", justify="right", no_wrap=True)
    table.add_column("Avg", justify="right", no_wrap=True)
    table.add_column("Value", justify="right", no_wrap=True)
    for p in positions[:40]:
        table.add_row(
            truncate(p.address, 14),
            p.outcome or "—",
            f"{p.size:,.2f}",
            fmt_pct(p.avg_price) if p.avg_price is not None else "—",
            f"{p.current_value:,.2f}" if p.current_value is not None else "—",
        )
    return build_panel(title, table, border_style="bright_magenta")
