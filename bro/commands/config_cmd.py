"""bro config — View and edit Bro configuration."""

from __future__ import annotations

from bro.config.manager import get_config, get_config_manager
from bro.utils.console import console, print_banner, print_info, print_success
from bro.utils.logger import get_logger

logger = get_logger(__name__)

EDITABLE_FIELDS = [
    ("default_language", "Default Language"),
    ("default_framework", "Default Framework"),
    ("always_docker", "Always Docker"),
    ("always_git", "Always Git"),
    ("always_postgresql", "Always PostgreSQL"),
    ("always_redis", "Always Redis"),
    ("always_jwt", "Always JWT"),
    ("always_readme", "Always README"),
    ("always_testing", "Always Testing"),
    ("always_linter", "Always Linter"),
    ("always_formatter", "Always Formatter"),
    ("open_vscode_after", "Open VS Code After Creation"),
    ("ai_provider", "AI Provider"),
    ("ai_api_key", "AI API Key"),
    ("ai_model", "AI Model"),
    ("github_default_private", "GitHub Default Private"),
]


def run_config() -> None:
    """View and edit configuration."""
    print_banner()

    config = get_config()
    manager = get_config_manager()

    console.print("\n[bold cyan]⚙️  Bro Configuration[/bold cyan]\n")

    for field_name, display_name in EDITABLE_FIELDS:
        value = getattr(config, field_name, "")
        # Mask sensitive values
        if "key" in field_name.lower() and value:
            display_value = value[:8] + "..." + value[-4:] if len(str(value)) > 12 else "****"
        else:
            display_value = str(value)
        console.print(f"  [dim]{display_name:<30}[/dim] [bold]{display_value}[/bold]")

    console.print()
    console.print("[dim]Edit a setting? Enter field name (or 'q' to quit)[/dim]")
    console.print()

    while True:
        try:
            field = console.input("[bold]Field [/bold][dim](or q)[/dim]: ").strip().lower()
            if field in ("q", "quit", "exit", ""):
                break

            # Find matching field
            matched = None
            for field_name, display_name in EDITABLE_FIELDS:
                if field in field_name.lower() or field in display_name.lower():
                    matched = field_name
                    break

            if not matched:
                console.print(f"[red]Unknown field: {field}[/red]")
                continue

            current = getattr(config, matched, "")
            console.print(f"  Current value: [dim]{current}[/dim]")
            new_value = console.input("  New value: ").strip()

            if not new_value:
                continue

            # Convert booleans
            if isinstance(current, bool):
                new_value = new_value.lower() in ("true", "yes", "1", "y")

            manager.update(**{matched: new_value})
            print_success(f"{matched} updated!")
            console.print()

        except KeyboardInterrupt:
            break

    print_info(f"Config saved to: [bold]{manager.config_path}[/bold]")
