"""Tests for bro check command."""

from unittest.mock import patch

from bro.commands.check import run_check


def test_run_check_executes() -> None:
    """Test that run_check executes without errors."""
    # Capture output by running check
    run_check()


def test_tool_checks_defined() -> None:
    """Test that tool checks are properly defined."""
    from bro.config.defaults import TOOL_CHECKS

    assert len(TOOL_CHECKS) > 0
    for name, info in TOOL_CHECKS.items():
        assert "command" in info
        assert "name" in info
