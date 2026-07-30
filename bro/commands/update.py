"""bro update — Update Bro, templates, and internal assets."""

from __future__ import annotations

from bro.utils.console import console, print_banner, print_error, print_info, print_success
from bro.utils.logger import get_logger
from bro.utils.process import run

logger = get_logger(__name__)


def run_update() -> None:
    """Update Bro and its assets."""
    print_banner()

    console.print("\n[bold cyan]🔄 Updating Bro[/bold cyan]\n")

    # Update via pipx
    print_info("Checking for Bro updates...")
    result = run("pipx upgrade bro", timeout=60)
    if result.success:
        print_success("Bro updated successfully!")
    else:
        # Fallback to pip
        result = run("pip install --upgrade bro", timeout=60)
        if result.success:
            print_success("Bro updated successfully!")
        else:
            print_error("Could not auto-update. Try: [bold]pipx upgrade bro[/bold]")

    # Update templates
    print_info("Templates are bundled with Bro and updated automatically.")

    console.print()
    print_success("Update complete! 🎉")
