"""Tests for TUI screens and markup."""

from bro.tui.screens.start import create_contact_footer


def test_contact_text_markup() -> None:
    """Verify create_contact_footer returns styled Text without errors."""
    text_obj = create_contact_footer()
    assert "Sameet Patro on LinkedIn" in text_obj.plain
