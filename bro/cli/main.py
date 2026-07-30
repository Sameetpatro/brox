"""CLI main — Typer application entry point with all commands registered."""

from __future__ import annotations

from typing import Annotated

import typer

from bro import __version__

app = typer.Typer(
    name="bro",
    help="🚀 Bro — The Developer Workspace Manager",
    no_args_is_help=True,
    rich_markup_mode="rich",
    pretty_exceptions_enable=True,
    add_completion=True,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        from bro.utils.console import console
        console.print(f"[bold cyan]Bro[/bold cyan] v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", help="Show version.", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """🚀 Bro — The Developer Workspace Manager.

    Create projects, save templates, reuse templates, learn project structures,
    clone repositories, and use AI to automate development tasks.
    """


# ─── Commands ─────────────────────────────────────────────────────────────────


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
