"""Base Textual app for Bro TUI."""

from __future__ import annotations

from pathlib import Path

from textual.app import App

# Path to the TCSS file
STYLES_PATH = Path(__file__).parent / "styles" / "app.tcss"


class BroApp(App[None]):
    """Base Textual application for all Bro TUI screens."""

    TITLE = "Bro"
    SUB_TITLE = "Developer Workspace Manager"
    CSS_PATH = STYLES_PATH

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("escape", "back", "Back"),
    ]

    def action_back(self) -> None:
        """Go back / pop screen."""
        if len(self.screen_stack) > 1:
            self.pop_screen()
        else:
            self.exit()
