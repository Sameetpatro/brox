"""bro delete — Delete a saved template."""

from __future__ import annotations

import shutil

from bro.commands.use import _list_templates
from bro.config.defaults import TEMPLATES_DIR
from bro.utils.console import console, print_banner, print_error, print_info, print_success
from bro.utils.logger import get_logger

logger = get_logger(__name__)


def run_delete() -> None:
    """Delete a saved template."""
    print_banner()

    templates = _list_templates()
    if not templates:
        print_info("No saved templates found.")
        return

    console.print("\n[bold cyan]🗑️  Delete Template[/bold cyan]\n")
    for i, (name, config) in enumerate(templates, 1):
        console.print(f"  [{i}] [bold]{name}[/bold]  [dim]{config.description}[/dim]")

    console.print()
    try:
        choice = console.input("[bold]Select template to delete [/bold][dim](number)[/dim]: ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(templates):
            print_error("Invalid choice.")
            return
    except (ValueError, KeyboardInterrupt):
        print_info("Cancelled.")
        return

    name, _ = templates[idx]

    try:
        confirm = console.input(f"[yellow]Delete '{name}'? (y/n)[/yellow] ")
        if confirm.lower() != "y":
            print_info("Cancelled.")
            return
    except KeyboardInterrupt:
        return

    template_dir = TEMPLATES_DIR / name
    if template_dir.exists():
        shutil.rmtree(template_dir)
        print_success(f"Template [bold]{name}[/bold] deleted.")
    else:
        print_error(f"Template '{name}' not found.")
