"""Process utilities — subprocess runners with logging."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from bro.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CommandResult:
    """Result of running a command."""

    returncode: int
    stdout: str = ""
    stderr: str = ""
    success: bool = field(init=False)

    def __post_init__(self) -> None:
        self.success = self.returncode == 0


def run(
    command: str | list[str],
    cwd: Path | str | None = None,
    timeout: int = 120,
    capture: bool = True,
    env: dict[str, str] | None = None,
) -> CommandResult:
    """Run a command and return the result."""
    cmd_str = " ".join(command) if isinstance(command, list) else command

    logger.debug("Running: %s (cwd=%s)", cmd_str, cwd)

    try:
        result = subprocess.run(
            command,
            shell=isinstance(command, str),
            cwd=str(cwd) if cwd else None,
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=env,
        )
        return CommandResult(
            returncode=result.returncode,
            stdout=result.stdout.strip() if result.stdout else "",
            stderr=result.stderr.strip() if result.stderr else "",
        )
    except subprocess.TimeoutExpired:
        logger.error("Command timed out after %ds: %s", timeout, cmd_str)
        return CommandResult(returncode=-1, stderr=f"Timed out after {timeout}s")
    except FileNotFoundError:
        logger.error("Command not found: %s", cmd_str)
        return CommandResult(returncode=-1, stderr="Command not found")
    except OSError as e:
        logger.error("OS error running command: %s", e)
        return CommandResult(returncode=-1, stderr=str(e))


def run_streaming(
    command: str | list[str],
    cwd: Path | str | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.Popen[str]:
    """Run a command with streaming output (for long-running processes)."""
    return subprocess.Popen(
        command,
        shell=isinstance(command, str),
        cwd=str(cwd) if cwd else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
