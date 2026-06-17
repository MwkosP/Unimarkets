"""Showcase: track a Polymarket user and infer their trading style.

Run:
    uv run examples/user_tracking.py
    uv run examples/user_tracking.py 0xYourWalletAddress
"""

from __future__ import annotations

import sys
from typing import Any

from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from unipmx import Polymarket, display

DEFAULT_USER = "0x7c3db723f1d4d8cb9c550095203b686cb11e5c6b"


console = Console()
failures: list[tuple[str, str]] = []


def safe(label: str, fn, fallback: Any = None):
    """Keep the example useful even if one public endpoint is blocked."""
    try:
        return fn()
    except Exception as exc:  # noqa: BLE001 - examples should keep going.
        failures.append((label, str(exc)))
        return fallback


def unavailable_panel() -> Panel:
    table = Table(show_header=False, box=None)
    table.add_column("Endpoint", style="dim")
    table.add_column("Reason")
    for label, reason in failures:
        table.add_row(label, reason)

    message = (
        "No live Polymarket user data was loaded, so trader style was not inferred. "
        "Try again after connecting a VPN or network where Polymarket's public Data/Gamma APIs return JSON."
    )
    return Panel(Group(Text(message), table), title="Data Unavailable", border_style="yellow")


def main() -> None:
    user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_USER
    client = Polymarket()

    console.rule(f"[bold]Polymarket User Tracking[/bold] {user}")

    style = safe("style", lambda: client.findUserStyle(user), None)
    if style is not None:
        display(style)
    elif failures:
        console.print(unavailable_panel())


if __name__ == "__main__":
    main()
