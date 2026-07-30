"""Template registry — discovers and loads built-in templates."""

from __future__ import annotations

from pathlib import Path

from bro.models.language import Framework, Language
from bro.utils.logger import get_logger

logger = get_logger(__name__)

BUILTIN_DIR = Path(__file__).parent / "builtin"


def discover_builtin_templates() -> dict[tuple[str, str], Path]:
    """Discover all built-in templates. Returns {(language, framework): path}."""
    templates: dict[tuple[str, str], Path] = {}

    if not BUILTIN_DIR.exists():
        return templates

    for lang_dir in BUILTIN_DIR.iterdir():
        if not lang_dir.is_dir():
            continue
        for fw_dir in lang_dir.iterdir():
            if not fw_dir.is_dir():
                continue
            config_file = fw_dir / "template.yaml"
            if config_file.exists():
                templates[(lang_dir.name, fw_dir.name)] = fw_dir

    return templates


def get_builtin_template(language: Language, framework: Framework) -> Path | None:
    """Get the path to a built-in template."""
    templates = discover_builtin_templates()
    key = (language.value, framework.value)
    return templates.get(key)
