"""Template configuration model — for saved/user templates."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field

from bro.models.language import Framework, Language


class TemplateConfig(BaseModel):
    """Metadata for a saved project template."""

    name: str = Field(..., description="Template name")
    description: str = Field(default="", description="Template description")
    language: Language | None = Field(default=None, description="Primary language")
    framework: Framework | None = Field(default=None, description="Framework used")
    author: str = Field(default="", description="Template author")
    version: str = Field(default="1.0.0", description="Template version")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)
    placeholders: dict[str, str] = Field(
        default_factory=dict,
        description="Mapping of original values to placeholder names",
    )
    ignore_patterns: list[str] = Field(
        default_factory=lambda: [
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
        ],
    )
    source_path: str = Field(default="", description="Original project path")

    @property
    def display_label(self) -> str:
        """Formatted label for display in template browser."""
        parts = [self.name]
        if self.language:
            parts.append(f"({self.language.display_name})")
        if self.framework:
            parts.append(f"[{self.framework.display_name}]")
        return " ".join(parts)


class TemplateFile(BaseModel):
    """A single file within a template."""

    relative_path: str = Field(..., description="Path relative to template root")
    content: str = Field(default="", description="File content (may contain Jinja2 placeholders)")
    is_binary: bool = Field(default=False, description="Whether this is a binary file")
    binary_path: str | None = Field(default=None, description="Path to binary file if binary")


class TemplateManifest(BaseModel):
    """Complete template package — config + files."""

    config: TemplateConfig
    files: list[TemplateFile] = Field(default_factory=list)
    template_dir: Path | None = None

    model_config = {"arbitrary_types_allowed": True}
