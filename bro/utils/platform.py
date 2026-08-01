"""Platform utilities — cross-platform detection and helpers."""

from __future__ import annotations

import platform
import shutil
import subprocess
from enum import StrEnum


class OS(StrEnum):
    """Operating system detection."""

    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"
    UNKNOWN = "unknown"


def get_os() -> OS:
    """Detect the current operating system."""
    system = platform.system().lower()
    mapping = {"darwin": OS.MACOS, "windows": OS.WINDOWS, "linux": OS.LINUX}
    return mapping.get(system, OS.UNKNOWN)


def is_command_available(command: str) -> bool:
    """Check if a command is available on the system PATH."""
    return shutil.which(command) is not None


def run_command_silent(command: str) -> tuple[bool, str]:
    """Run a command silently and return (success, output)."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15,
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False, ""


def get_tool_version(command: str) -> str | None:
    """Get the version string from a tool's version command."""
    success, output = run_command_silent(command)
    if success and output:
        # Extract version-like string from output
        return output.split("\n")[0].strip()
    return None


def open_in_vscode(path: str) -> bool:
    """Open a path in VS Code."""
    if is_command_available("code"):
        try:
            subprocess.Popen(["code", path])
            return True
        except OSError:
            pass
    return False


def open_url(url: str) -> None:
    """Open a URL in the default browser."""
    import webbrowser

    webbrowser.open(url)
