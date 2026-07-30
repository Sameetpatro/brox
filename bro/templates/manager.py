"""Template manager — Save, load, delete user templates from ~/.bro/templates/."""

from __future__ import annotations

from pathlib import Path

import yaml

from bro.config.defaults import TEMPLATES_DIR
from bro.models.template import TemplateConfig
from bro.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateManager:
    """Manages user-saved templates in ~/.bro/templates/."""

    def __init__(self, templates_dir: Path | None = None) -> None:
        self.templates_dir = templates_dir or TEMPLATES_DIR

    def list_templates(self) -> list[TemplateConfig]:
        """List all saved templates."""
        templates: list[TemplateConfig] = []
        if not self.templates_dir.exists():
            return templates

        for template_dir in sorted(self.templates_dir.iterdir()):
            if template_dir.is_dir():
                config_file = template_dir / "template.yaml"
                if config_file.exists():
                    try:
                        data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
                        templates.append(TemplateConfig(**data))
                    except Exception as e:
                        logger.warning("Failed to load template %s: %s", template_dir.name, e)
        return templates

    def get_template(self, name: str) -> TemplateConfig | None:
        """Get a specific template by name."""
        config_file = self.templates_dir / name / "template.yaml"
        if config_file.exists():
            data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
            return TemplateConfig(**data)
        return None

    def get_template_dir(self, name: str) -> Path | None:
        """Get the directory for a template."""
        path = self.templates_dir / name
        return path if path.exists() else None

    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        import shutil

        path = self.templates_dir / name
        if path.exists():
            shutil.rmtree(path)
            return True
        return False
