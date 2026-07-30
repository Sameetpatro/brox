"""Console — Rich console singleton for beautiful output."""

from __future__ import annotations

from rich.console import Console
from rich.theme import Theme

# ─── Custom theme ─────────────────────────────────────────────────────────────

BRO_THEME = Theme(
    {
        "bro.title": "bold cyan",
        "bro.success": "bold green",
        "bro.error": "bold red",
        "bro.warning": "bold yellow",
        "bro.info": "bold blue",
        "bro.muted": "dim white",
        "bro.highlight": "bold magenta",
        "bro.path": "underline cyan",
        "bro.command": "bold white on grey23",
    }
)

# Singleton console
console = Console(theme=BRO_THEME)
error_console = Console(theme=BRO_THEME, stderr=True)


def print_banner() -> None:
    """Print the Bro ASCII banner."""
    banner = r"""
[bold cyan]
  ██████╗ ██████╗  ██████╗
  ██╔══██╗██╔══██╗██╔═══██╗
  ██████╔╝██████╔╝██║   ██║
  ██╔══██╗██╔══██╗██║   ██║
  ██████╔╝██║  ██║╚██████╔╝
  ╚═════╝ ╚═╝  ╚═╝ ╚═════╝
[/bold cyan]
[dim]  Developer Workspace Manager[/dim]
    """
    console.print(banner)


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"  [bro.success]✓[/bro.success] {message}")


def print_error(message: str) -> None:
    """Print an error message."""
    console.print(f"  [bro.error]✗[/bro.error] {message}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    console.print(f"  [bro.warning]⚠[/bro.warning] {message}")


def print_info(message: str) -> None:
    """Print an info message."""
    console.print(f"  [bro.info]ℹ[/bro.info] {message}")


def print_step(step: int, total: int, message: str) -> None:
    """Print a step progress message."""
    console.print(f"  [bro.muted][{step}/{total}][/bro.muted] {message}")
