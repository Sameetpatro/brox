"""bro clone — Clone a repository with analysis and post-clone options."""

from __future__ import annotations

from pathlib import Path

from bro.commands.follow_cmd import analyze_project, display_analysis
from bro.utils.console import console, print_banner, print_error, print_info, print_success
from bro.utils.logger import get_logger
from bro.utils.platform import open_in_vscode
from bro.utils.process import run

logger = get_logger(__name__)


def run_clone() -> None:
    """Execute the clone command."""
    print_banner()
    console.print("\n[bold cyan]📥 Clone Repository[/bold cyan]\n")

    # Ask for URL
    try:
        url = console.input("  [bold]GitHub Repository URL: [/bold]")
        if not url.strip():
            print_error("URL cannot be empty.")
            return
    except KeyboardInterrupt:
        print_info("Cancelled.")
        return

    url = url.strip()

    # Ask for project root
    console.print()
    console.print("  [bold]Project Root Folder:[/bold]")
    console.print("  [1] Default (repository name)")
    console.print("  [2] Custom name")
    console.print()

    try:
        choice = console.input("  [bold]Choice [/bold][dim](1/2)[/dim]: ")
    except KeyboardInterrupt:
        print_info("Cancelled.")
        return

    clone_dir: str | None = None
    if choice.strip() == "2":
        try:
            clone_dir = console.input("  [bold]Folder name: [/bold]").strip()
        except KeyboardInterrupt:
            print_info("Cancelled.")
            return

    # Clone
    cmd = f"git clone {url}"
    if clone_dir:
        cmd += f" {clone_dir}"

    console.print()
    print_info("Cloning repository...")

    result = run(cmd, cwd=Path.cwd(), timeout=120)

    if not result.success:
        print_error(f"Clone failed: {result.stderr}")
        return

    # Determine cloned directory
    if clone_dir:
        project_dir = Path.cwd() / clone_dir
    else:
        # Extract repo name from URL
        repo_name = url.rstrip("/").rstrip(".git").split("/")[-1]
        project_dir = Path.cwd() / repo_name

    if not project_dir.exists():
        print_error("Could not find cloned directory.")
        return

    print_success(f"Repository cloned to [bold]{project_dir}[/bold]")
    console.print()

    # Analyze
    print_info("Analyzing project...")
    analysis = analyze_project(project_dir)
    display_analysis(analysis)

    # Post-clone options
    console.print()
    console.print("[bold cyan]What would you like to do?[/bold cyan]")
    console.print()
    console.print("  [1] Open Project in VS Code")
    console.print("  [2] Learn as Template")
    console.print("  [3] Explain Architecture")
    console.print("  [4] Exit")
    console.print()

    try:
        action = console.input("[bold]Choice [/bold][dim](1-4)[/dim]: ")
    except KeyboardInterrupt:
        return

    if action.strip() == "1":
        if open_in_vscode(str(project_dir)):
            print_success("Opened in VS Code!")
        else:
            print_error("VS Code not found. Install it or use 'code' command.")
    elif action.strip() == "2":
        console.print()
        try:
            name = console.input("[bold]Template name: [/bold]").strip()
            if name:
                import os

                from bro.commands.save import run_save
                os.chdir(project_dir)
                run_save(template_name=name)
        except KeyboardInterrupt:
            pass
    elif action.strip() == "3":
        _explain_architecture(analysis)


def _explain_architecture(analysis: object) -> None:
    """Explain the project architecture."""
    from rich.panel import Panel

    from bro.models.project import ProjectAnalysis

    if not isinstance(analysis, ProjectAnalysis):
        return

    explanation = []
    if analysis.language:
        explanation.append(f"This is a [bold]{analysis.language.display_name}[/bold] project")
    if analysis.framework:
        explanation.append(f"using the [bold]{analysis.framework.display_name}[/bold] framework")
    if analysis.has_docker:
        explanation.append("with Docker containerization")
    if analysis.has_postgresql:
        explanation.append("backed by PostgreSQL")
    if analysis.has_redis:
        explanation.append("with Redis for caching/sessions")
    if analysis.has_github_actions:
        explanation.append("using GitHub Actions for CI/CD")
    if analysis.has_testing:
        explanation.append("with an established testing setup")

    text = ", ".join(explanation) + "." if explanation else "Architecture analysis unavailable."
    console.print(Panel(text, title="[bold]Architecture Overview[/bold]", border_style="cyan"))
