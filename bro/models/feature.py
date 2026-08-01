"""Feature definitions — toggleable project features."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class Feature(StrEnum):
    """Selectable project features."""

    GIT = "git"
    DOCKER = "docker"
    DOCKER_COMPOSE = "docker-compose"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    JWT = "jwt"
    SWAGGER = "swagger"
    GITHUB_ACTIONS = "github-actions"
    PRE_COMMIT = "pre-commit"
    README = "readme"
    DOTENV = "dotenv"
    TESTING = "testing"
    FORMATTER = "formatter"
    LINTER = "linter"
    VSCODE = "vscode"
    LICENSE = "license"
    MAKEFILE = "makefile"
    EDITORCONFIG = "editorconfig"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names: dict[str, str] = {
            "git": "Git",
            "docker": "Docker",
            "docker-compose": "Docker Compose",
            "postgresql": "PostgreSQL",
            "redis": "Redis",
            "jwt": "JWT Authentication",
            "swagger": "Swagger / OpenAPI",
            "github-actions": "GitHub Actions CI",
            "pre-commit": "Pre-commit Hooks",
            "readme": "README.md",
            "dotenv": ".env File",
            "testing": "Testing Framework",
            "formatter": "Code Formatter",
            "linter": "Linter",
            "vscode": "VS Code Settings",
            "license": "License (MIT)",
            "makefile": "Makefile",
            "editorconfig": "EditorConfig",
        }
        return names.get(self.value, self.value.title())

    @property
    def description(self) -> str:
        """Short description for feature selection UI."""
        descriptions: dict[str, str] = {
            "git": "Initialize a git repository",
            "docker": "Generate a production Dockerfile",
            "docker-compose": "Docker Compose with services",
            "postgresql": "PostgreSQL database configuration",
            "redis": "Redis cache/store configuration",
            "jwt": "JWT-based authentication setup",
            "swagger": "API documentation with Swagger",
            "github-actions": "CI/CD pipeline with GitHub Actions",
            "pre-commit": "Pre-commit hooks for code quality",
            "readme": "Professional README with badges",
            "dotenv": "Environment variable configuration",
            "testing": "Testing framework and sample tests",
            "formatter": "Code formatting (Black/Prettier/etc.)",
            "linter": "Linting (Ruff/ESLint/etc.)",
            "vscode": "VS Code workspace settings & extensions",
            "license": "MIT License file",
            "makefile": "Makefile with common commands",
            "editorconfig": "EditorConfig for consistent coding styles",
        }
        return descriptions.get(self.value, "")

    @property
    def icon(self) -> str:
        """Emoji icon for display."""
        icons: dict[str, str] = {
            "git": "🔀",
            "docker": "🐳",
            "docker-compose": "🐳",
            "postgresql": "🐘",
            "redis": "🔴",
            "jwt": "🔐",
            "swagger": "📖",
            "github-actions": "⚡",
            "pre-commit": "🪝",
            "readme": "📝",
            "dotenv": "🔧",
            "testing": "🧪",
            "formatter": "✨",
            "linter": "🔍",
            "vscode": "💻",
            "license": "📄",
            "makefile": "⚙️",
            "editorconfig": "📐",
        }
        return icons.get(self.value, "📦")


class FeatureInfo(BaseModel):
    """Extended metadata for a feature."""

    feature: Feature
    default_enabled: bool = False
    requires: list[Feature] = []  # Dependencies on other features

    @property
    def display_name(self) -> str:
        return self.feature.display_name

    @property
    def description(self) -> str:
        return self.feature.description


# ─── Default feature configurations ──────────────────────────────────────────

DEFAULT_FEATURES: list[FeatureInfo] = [
    FeatureInfo(feature=Feature.GIT, default_enabled=True),
    FeatureInfo(feature=Feature.README, default_enabled=True),
    FeatureInfo(feature=Feature.DOTENV, default_enabled=True),
    FeatureInfo(feature=Feature.LICENSE, default_enabled=True),
    FeatureInfo(feature=Feature.EDITORCONFIG, default_enabled=True),
    FeatureInfo(feature=Feature.LINTER, default_enabled=True),
    FeatureInfo(feature=Feature.FORMATTER, default_enabled=True),
    FeatureInfo(feature=Feature.TESTING, default_enabled=True),
    FeatureInfo(feature=Feature.DOCKER, default_enabled=False),
    FeatureInfo(feature=Feature.DOCKER_COMPOSE, default_enabled=False, requires=[Feature.DOCKER]),
    FeatureInfo(feature=Feature.POSTGRESQL, default_enabled=False),
    FeatureInfo(feature=Feature.REDIS, default_enabled=False),
    FeatureInfo(feature=Feature.JWT, default_enabled=False),
    FeatureInfo(feature=Feature.SWAGGER, default_enabled=False),
    FeatureInfo(feature=Feature.GITHUB_ACTIONS, default_enabled=False),
    FeatureInfo(feature=Feature.PRE_COMMIT, default_enabled=False, requires=[Feature.GIT]),
    FeatureInfo(feature=Feature.VSCODE, default_enabled=False),
    FeatureInfo(feature=Feature.MAKEFILE, default_enabled=False),
]


def get_default_features() -> list[Feature]:
    """Return list of features that are enabled by default."""
    return [fi.feature for fi in DEFAULT_FEATURES if fi.default_enabled]
