"""bro check — Verify development tool installations."""

from __future__ import annotations

from rich.panel import Panel
from rich.table import Table

from bro.config.defaults import TOOL_CHECKS
from bro.utils.console import console, print_banner
from bro.utils.platform import get_os, run_command_silent


def run_check() -> None:
    """Check which development tools are installed."""
    print_banner()

    table = Table(
        title="🔍 System Health Check",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        title_style="bold white",
        padding=(0, 2),
    )
    table.add_column("Tool", style="bold white", min_width=14)
    table.add_column("Status", justify="center", min_width=10)
    table.add_column("Version", style="dim", min_width=30)

    installed_count = 0
    total_count = len(TOOL_CHECKS)

    for tool_name, info in TOOL_CHECKS.items():
        success, output = run_command_silent(info["command"])
        if success:
            installed_count += 1
            status = "[bold green]✓ Installed[/bold green]"
            version = output.split("\n")[0][:50] if output else "—"
        else:
            status = "[bold red]✗ Missing[/bold red]"
            version = "[dim]Not found[/dim]"

        table.add_row(tool_name, status, version)

    console.print()
    console.print(table)
    console.print()

    # Summary
    os_name = get_os().value.title()
    if installed_count == total_count:
        summary = f"[bold green]All {total_count} tools installed![/bold green] 🎉"
    elif installed_count >= total_count * 0.7:
        missing = total_count - installed_count
        summary = f"[bold yellow]{installed_count}/{total_count} tools installed.[/bold yellow] {missing} missing."
    else:
        missing = total_count - installed_count
        summary = f"[bold red]{installed_count}/{total_count} tools installed.[/bold red] {missing} missing."

    console.print(
        Panel(
            f"  Platform: [bold]{os_name}[/bold]\n  {summary}",
            title="[bold white]Summary[/bold white]",
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()
