"""Logger setup — structured logging for Bro."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_CONFIGURED = False


def setup_logging(verbose: bool = False, log_file: Path | None = None) -> None:
    """Configure the root logger for Bro."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s │ %(levelname)-8s │ %(name)s │ %(message)s"
    date_fmt = "%H:%M:%S"

    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stderr)]

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))

    logging.basicConfig(level=level, format=fmt, datefmt=date_fmt, handlers=handlers)

    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Get a named logger."""
    return logging.getLogger(name)
