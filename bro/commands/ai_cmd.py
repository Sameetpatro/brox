"""bro ai command — AI-powered development assistant."""

from __future__ import annotations

import json
from pathlib import Path

from bro.ai.client import get_ai_client
from bro.ai.prompts import BUILD_SYSTEM_PROMPT, DEBUG_SYSTEM_PROMPT, IMPROVE_SYSTEM_PROMPT
from bro.commands.follow_cmd import analyze_project, display_analysis
from bro.utils.console import console, print_banner, print_error, print_info
from bro.utils.logger import get_logger

logger = get_logger(__name__)


def run_ai() -> None:
    """Launch AI assistant menu."""
    print_banner()

    client = get_ai_client()
    if not client.is_available():
        print_error("AI features require an API key.")
        print_info("Set it with: [bold]bro config[/bold]")
        print_info("Or set environment variable: [bold]OPENAI_API_KEY[/bold]")
        return

    console.print("\n[bold cyan]🤖 Bro AI Assistant[/bold cyan]\n")
    console.print("  [1] 🏗️  Build Something")
    console.print("  [2] 🐛 Debug Project")
    console.print("  [3] ⚡ Improve Project")
    console.print("  [4] 🚪 Exit")
    console.print()

    try:
        choice = console.input("[bold]Choice [/bold][dim](1-4)[/dim]: ")
    except KeyboardInterrupt:
        return

    if choice.strip() == "1":
        _build_something(client)
    elif choice.strip() == "2":
        _debug_project(client)
    elif choice.strip() == "3":
        _improve_project(client)


def _build_something(client: object) -> None:
    """AI Build Something flow."""
    from bro.ai.client import AIClient

    if not isinstance(client, AIClient):
        return

    console.print("\n[bold cyan]🏗️  Build Something[/bold cyan]\n")
    console.print("[dim]Describe what you want to build:[/dim]\n")

    try:
        description = console.input("  > ")
        if not description.strip():
            return
    except KeyboardInterrupt:
        return

    print_info("Analyzing your request...")

    response = client.chat([
        {"role": "system", "content": BUILD_SYSTEM_PROMPT},
        {"role": "user", "content": description},
    ])

    try:
        # Parse AI response
        plan = json.loads(response)

        console.print("\n[bold cyan]📋 AI Project Plan[/bold cyan]\n")
        console.print(f"  [dim]Language:[/dim]    [bold]{plan.get('language', 'python')}[/bold]")
        console.print(f"  [dim]Framework:[/dim]   [bold]{plan.get('framework', 'fastapi')}[/bold]")
        console.print(f"  [dim]Features:[/dim]    {', '.join(plan.get('features', []))}")
        console.print(f"  [dim]Packages:[/dim]    {', '.join(plan.get('packages', []))}")
        if plan.get('description'):
            console.print(f"\n  [dim]{plan['description']}[/dim]")
        if plan.get('architecture_notes'):
            console.print(f"  [dim]{plan['architecture_notes']}[/dim]")

        console.print()
        try:
            confirm = console.input("[bold]Generate project? (y/n)[/bold] ")
            if confirm.lower() != "y":
                print_info("Cancelled.")
                return
        except KeyboardInterrupt:
            return

        # Ask for project name
        try:
            project_name = console.input("[bold]Project name: [/bold]").strip()
            if not project_name:
                return
        except KeyboardInterrupt:
            return

        # Build ProjectConfig and generate
        import contextlib

        from bro.generators.project import ProjectGenerator
        from bro.models.feature import Feature
        from bro.models.language import Framework, Language
        from bro.models.project import ProjectConfig

        features = []
        for f_name in plan.get("features", []):
            with contextlib.suppress(ValueError):
                features.append(Feature(f_name))

        config = ProjectConfig(
            name=project_name,
            display_name=project_name.replace("-", " ").title(),
            language=Language(plan.get("language", "python")),
            framework=Framework(plan.get("framework", "fastapi")),
            features=features,
            output_dir=Path.cwd(),
        )

        generator = ProjectGenerator()
        generator.generate(config)

    except json.JSONDecodeError:
        console.print(f"\n[bold]AI Response:[/bold]\n{response}")


def _debug_project(client: object) -> None:
    """AI Debug Project flow."""
    from bro.ai.client import AIClient

    if not isinstance(client, AIClient):
        return

    console.print("\n[bold cyan]🐛 Debug Project[/bold cyan]\n")
    console.print("  [1] Runtime Error")
    console.print("  [2] Build Error")
    console.print("  [3] Docker Issue")
    console.print("  [4] Dependency Issue")
    console.print()

    try:
        console.input("[bold]Issue type [/bold][dim](1-4)[/dim]: ")
    except KeyboardInterrupt:
        return

    console.print()
    try:
        error_info = console.input("[bold]Paste error/log (or describe the issue):[/bold]\n> ")
    except KeyboardInterrupt:
        return

    # Gather project context
    root = Path.cwd()
    analysis = analyze_project(root)

    context = f"""Project: {(analysis.language and analysis.language.value) or 'unknown'} / {(analysis.framework and analysis.framework.value) or 'unknown'}
Has Docker: {analysis.has_docker}
Has PostgreSQL: {analysis.has_postgresql}
Has Redis: {analysis.has_redis}

Error/Issue:
{error_info}"""

    print_info("Analyzing...")
    response = client.chat([
        {"role": "system", "content": DEBUG_SYSTEM_PROMPT},
        {"role": "user", "content": context},
    ])

    console.print(f"\n[bold cyan]💡 Solution[/bold cyan]\n\n{response}\n")


def _improve_project(client: object) -> None:
    """AI Improve Project flow."""
    from bro.ai.client import AIClient

    if not isinstance(client, AIClient):
        return

    console.print("\n[bold cyan]⚡ Improve Project[/bold cyan]\n")

    root = Path.cwd()
    analysis = analyze_project(root)
    display_analysis(analysis)

    context = f"""Language: {(analysis.language and analysis.language.value) or 'unknown'}
Framework: {(analysis.framework and analysis.framework.value) or 'unknown'}
Has Docker: {analysis.has_docker}
Has Docker Compose: {analysis.has_docker_compose}
Has PostgreSQL: {analysis.has_postgresql}
Has Redis: {analysis.has_redis}
Has JWT: {analysis.has_jwt}
Has Swagger: {analysis.has_swagger}
Has GitHub Actions: {analysis.has_github_actions}
Has Testing: {analysis.has_testing}
Has Linter: {analysis.has_linter}
Has Formatter: {analysis.has_formatter}
Config files: {', '.join(analysis.config_files)}"""

    print_info("Analyzing project for improvements...")
    response = client.chat([
        {"role": "system", "content": IMPROVE_SYSTEM_PROMPT},
        {"role": "user", "content": context},
    ])

    console.print(f"\n[bold cyan]📊 Improvement Suggestions[/bold cyan]\n\n{response}\n")
