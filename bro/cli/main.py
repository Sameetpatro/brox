"""CLI main — Typer application entry point with all commands registered."""

from __future__ import annotations

from typing import Annotated

import typer

from bro import __version__

app = typer.Typer(
    name="broz",
    help="🚀 Broz — The Developer Workspace Manager",
    no_args_is_help=False,
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    add_completion=True,
)


def print_help() -> None:
    """Print custom styled help screen with commands and author credits."""
    from rich.panel import Panel
    from rich.table import Table

    from bro.utils.console import console

    console.print()
    console.print(
        Panel(
            "[bold cyan]🚀 Broz — The Developer Workspace Manager[/bold cyan]\n"
            "[dim]Create, template, learn, clone, and AI-assist your projects.[/dim]\n\n"
            "[bold green]Sameet Patro built this[/bold green] ❤️\n"
            "[dim]🔗 LinkedIn:[/dim] [link=https://www.linkedin.com/in/sameet-patro/][underline cyan]https://www.linkedin.com/in/sameet-patro/[/underline cyan][/link]",
            title="[bold yellow]About Broz[/bold yellow]",
            subtitle="[dim]by Sameet Patro[/dim]",
            border_style="cyan",
        )
    )

    table = Table(title="Available Commands", border_style="dim", header_style="bold cyan")
    table.add_column("Command", style="bold yellow", width=12)
    table.add_column("Description", style="white")

    table.add_row("start", "🏗️  Create a new project with interactive wizard")
    table.add_row("follow", "👀 Enter Learning Mode — analyze current project structure")
    table.add_row("save", "💾 Save current project as a reusable template")
    table.add_row("use", "📦 Create a project from a saved template")
    table.add_row("delete", "🗑️  Delete a saved template")
    table.add_row("clone", "📥 Clone a repository with analysis and options")
    table.add_row("check", "🔍 Check installed development tools")
    table.add_row("config", "⚙️  View and edit Bro configuration")
    table.add_row("update", "🔄 Update Bro, templates, and internal assets")
    table.add_row("ai", "🤖 Launch AI-powered development assistant")
    table.add_row("help", "❓ Show this help message and author credits")

    console.print(table)
    console.print("\n[dim]Usage:[/dim] [bold cyan]bro <command> [options][/bold cyan]\n")


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        from bro.utils.console import console
        console.print(f"[bold cyan]Broz[/bold cyan] v{__version__}")
        raise typer.Exit()


def help_callback(value: bool) -> None:
    """Show help screen and exit."""
    if value:
        print_help()
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", help="Show version.", callback=version_callback, is_eager=True),
    ] = None,
    help_opt: Annotated[
        bool | None,
        typer.Option("-help", "--help", "-h", help="Show help screen.", callback=help_callback, is_eager=True),
    ] = None,
) -> None:
    """🚀 Broz — The Developer Workspace Manager."""
    if ctx.invoked_subcommand is None:
        print_help()


# ─── Commands ─────────────────────────────────────────────────────────────────


@app.command("help")
def show_help_cmd() -> None:
    """❓ Show all commands and author info."""
    print_help()


@app.command()
def start(
    project_name: Annotated[str, typer.Argument(help="Name of the project to create.")],
    quick: Annotated[
        bool,
        typer.Option("--quick", "-q", help="Quick mode — only ask language & framework."),
    ] = False,
    output_dir: Annotated[
        str | None,
        typer.Option("--output", "-o", help="Output directory (default: current dir)."),
    ] = None,
) -> None:
    """🏗️  Create a new project with an interactive wizard."""
    from bro.commands.start import run_start
    run_start(project_name=project_name, quick=quick, output_dir=output_dir)


@app.command()
def follow() -> None:
    """👀 Enter Learning Mode — analyze current project structure."""
    from bro.commands.follow_cmd import run_follow
    run_follow()


@app.command()
def save(
    template_name: Annotated[str, typer.Argument(help="Name for the saved template.")],
) -> None:
    """💾 Save current project as a reusable template."""
    from bro.commands.save import run_save
    run_save(template_name=template_name)


@app.command()
def use() -> None:
    """📦 Create a project from a saved template."""
    from bro.commands.use import run_use
    run_use()


@app.command()
def delete() -> None:
    """🗑️  Delete a saved template."""
    from bro.commands.delete import run_delete
    run_delete()


@app.command()
def clone() -> None:
    """📥 Clone a repository with analysis and options."""
    from bro.commands.clone_cmd import run_clone
    run_clone()


@app.command()
def check() -> None:
    """🔍 Check installed development tools."""
    from bro.commands.check import run_check
    run_check()


@app.command()
def config() -> None:
    """⚙️  View and edit Bro configuration."""
    from bro.commands.config_cmd import run_config
    run_config()


@app.command()
def update() -> None:
    """🔄 Update Bro, templates, and internal assets."""
    from bro.commands.update import run_update
    run_update()


@app.command()
def ai() -> None:
    """🤖 Launch AI-powered development assistant."""
    from bro.commands.ai_cmd import run_ai
    run_ai()
