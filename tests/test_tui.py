"""Tests for TUI screens and markup."""

from rich.markup import render
from bro.tui.screens.start import CONTACT_TEXT


def test_contact_text_markup() -> None:
    """Verify CONTACT_TEXT renders without Rich MarkupError."""
    result = render(CONTACT_TEXT)
    assert "Sameet Patro on LinkedIn" in result.plain
