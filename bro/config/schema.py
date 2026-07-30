"""Config schema — Pydantic model for ~/.bro/config.yaml."""

from __future__ import annotations

from pydantic import BaseModel, Field

from bro.models.feature import Feature
from bro.models.language import Framework, Language


class BroConfig(BaseModel):
    """Global Bro configuration stored in ~/.bro/config.yaml."""

    # Defaults for quick mode
    default_language: Language = Field(default=Language.PYTHON)
    default_framework: Framework = Field(default=Framework.FASTAPI)

    # Feature defaults (used by --quick)
    always_git: bool = Field(default=True)
    always_docker: bool = Field(default=False)
    always_docker_compose: bool = Field(default=False)
    always_postgresql: bool = Field(default=False)
    always_redis: bool = Field(default=False)
    always_jwt: bool = Field(default=False)
    always_readme: bool = Field(default=True)
    always_dotenv: bool = Field(default=True)
    always_testing: bool = Field(default=True)
    always_linter: bool = Field(default=True)
    always_formatter: bool = Field(default=True)
    always_license: bool = Field(default=True)
    always_editorconfig: bool = Field(default=True)
    always_swagger: bool = Field(default=False)
    always_github_actions: bool = Field(default=False)
    always_pre_commit: bool = Field(default=False)
    always_vscode: bool = Field(default=False)
    always_makefile: bool = Field(default=False)

    # GitHub
    github_token: str = Field(default="", description="Cached GitHub token")
    github_default_private: bool = Field(default=True)

    # AI
    ai_provider: str = Field(default="openai", description="AI provider: openai, anthropic, google")
    ai_api_key: str = Field(default="", description="API key for AI provider")
    ai_model: str = Field(default="gpt-4o", description="Model name")

    # General
    open_vscode_after: bool = Field(default=False, description="Open VS Code after project creation")
    default_output_dir: str = Field(default="", description="Default parent dir for new projects")

    def get_quick_features(self) -> list[Feature]:
        """Build feature list from 'always_*' config flags."""
        features: list[Feature] = []
        flag_map: dict[str, Feature] = {
            "always_git": Feature.GIT,
            "always_docker": Feature.DOCKER,
            "always_docker_compose": Feature.DOCKER_COMPOSE,
            "always_postgresql": Feature.POSTGRESQL,
            "always_redis": Feature.REDIS,
            "always_jwt": Feature.JWT,
            "always_readme": Feature.README,
            "always_dotenv": Feature.DOTENV,
            "always_testing": Feature.TESTING,
            "always_linter": Feature.LINTER,
            "always_formatter": Feature.FORMATTER,
            "always_license": Feature.LICENSE,
            "always_editorconfig": Feature.EDITORCONFIG,
            "always_swagger": Feature.SWAGGER,
            "always_github_actions": Feature.GITHUB_ACTIONS,
            "always_pre_commit": Feature.PRE_COMMIT,
            "always_vscode": Feature.VSCODE,
            "always_makefile": Feature.MAKEFILE,
        }
        for flag_name, feature in flag_map.items():
            if getattr(self, flag_name, False):
                features.append(feature)
        return features
