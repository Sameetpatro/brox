"""Config defaults — constants and paths."""

from __future__ import annotations

from pathlib import Path

# ─── Paths ────────────────────────────────────────────────────────────────────

BRO_HOME = Path.home() / ".bro"
CONFIG_FILE = BRO_HOME / "config.yaml"
TEMPLATES_DIR = BRO_HOME / "templates"
AUTH_FILE = BRO_HOME / "auth.yaml"
LOG_FILE = BRO_HOME / "bro.log"

# ─── Ignore patterns for template learning ────────────────────────────────────

DEFAULT_IGNORE_PATTERNS: list[str] = [
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "dist",
    "build",
    "target",
    ".idea",
    ".vscode",
    "coverage",
    "__pycache__",
    ".env",
    "logs",
    "*.pyc",
    ".DS_Store",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "*.egg-info",
    ".tox",
    ".nox",
]

# ─── Tool check commands ──────────────────────────────────────────────────────

TOOL_CHECKS: dict[str, dict[str, str]] = {
    "Python": {"command": "python3 --version", "name": "Python"},
    "Go": {"command": "go version", "name": "Go"},
    "Node.js": {"command": "node --version", "name": "Node.js"},
    "Git": {"command": "git --version", "name": "Git"},
    "Docker": {"command": "docker --version", "name": "Docker"},
    "Redis": {"command": "redis-cli --version", "name": "Redis"},
    "PostgreSQL": {"command": "psql --version", "name": "PostgreSQL"},
    "Java": {"command": "java --version", "name": "Java"},
    "Rust": {"command": "rustc --version", "name": "Rust"},
    "VS Code": {"command": "code --version", "name": "VS Code"},
    "uv": {"command": "uv --version", "name": "uv"},
    "GitHub CLI": {"command": "gh --version", "name": "GitHub CLI"},
    "Cargo": {"command": "cargo --version", "name": "Cargo"},
    "npm": {"command": "npm --version", "name": "npm"},
}
