"""Project configuration model — the central data object for project creation."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field

from bro.models.feature import Feature
from bro.models.language import Framework, Language


class ProjectConfig(BaseModel):
    """Complete configuration for a project to be generated."""

    # Core identity
    name: str = Field(..., description="Project name (used as directory name)")
    display_name: str = Field(default="", description="Human-readable project name")

    # Technology stack
    language: Language = Field(..., description="Primary programming language")
    framework: Framework = Field(..., description="Framework to use")

    # Features
    features: list[Feature] = Field(default_factory=list, description="Selected features")

    # GitHub
    create_github_repo: bool = Field(default=False, description="Create a GitHub repository")
    github_private: bool = Field(default=True, description="Make GitHub repo private")

    # Paths
    output_dir: Path = Field(default_factory=Path.cwd, description="Parent directory for the project")

    @property
    def project_dir(self) -> Path:
        """Full path to the project directory."""
        return self.output_dir / self.name

    @property
    def safe_name(self) -> str:
        """Python-safe project name (underscores instead of hyphens)."""
        return self.name.replace("-", "_")

    def has_feature(self, feature: Feature) -> bool:
        """Check if a feature is selected."""
        return feature in self.features

    model_config = {"arbitrary_types_allowed": True}


class ProjectAnalysis(BaseModel):
    """Result of analyzing an existing project's structure."""

    root_path: Path
    language: Language | None = None
    framework: Framework | None = None
    package_manager: str | None = None
    has_docker: bool = False
    has_docker_compose: bool = False
    has_postgresql: bool = False
    has_redis: bool = False
    has_github_actions: bool = False
    has_testing: bool = False
    has_linter: bool = False
    has_formatter: bool = False
    has_readme: bool = False
    has_license: bool = False
    has_makefile: bool = False
    has_editorconfig: bool = False
    has_git: bool = False
    has_env: bool = False
    has_vscode: bool = False
    has_pre_commit: bool = False
    has_jwt: bool = False
    has_swagger: bool = False
    dependencies: list[str] = Field(default_factory=list)
    directory_structure: dict[str, list[str]] = Field(default_factory=dict)
    config_files: list[str] = Field(default_factory=list)

    model_config = {"arbitrary_types_allowed": True}
