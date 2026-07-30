"""Template renderer — Jinja2 engine for rendering project templates."""

from __future__ import annotations

from pathlib import Path

import jinja2

from bro.models.project import ProjectConfig
from bro.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateRenderer:
    """Renders Jinja2 templates into project files."""

    def __init__(self) -> None:
        self.builtin_dir = Path(__file__).parent / "builtin"

    def _get_context(self, config: ProjectConfig) -> dict[str, object]:
        """Build the Jinja2 template context from project config."""
        from bro.models.feature import Feature

        return {
            "project_name": config.name,
            "project_name_safe": config.safe_name,
            "display_name": config.display_name or config.name,
            "language": config.language.value,
            "framework": config.framework.value,
            "has_docker": config.has_feature(Feature.DOCKER),
            "has_docker_compose": config.has_feature(Feature.DOCKER_COMPOSE),
            "has_postgresql": config.has_feature(Feature.POSTGRESQL),
            "has_redis": config.has_feature(Feature.REDIS),
            "has_jwt": config.has_feature(Feature.JWT),
            "has_swagger": config.has_feature(Feature.SWAGGER),
            "has_github_actions": config.has_feature(Feature.GITHUB_ACTIONS),
            "has_pre_commit": config.has_feature(Feature.PRE_COMMIT),
            "has_readme": config.has_feature(Feature.README),
            "has_dotenv": config.has_feature(Feature.DOTENV),
            "has_testing": config.has_feature(Feature.TESTING),
            "has_formatter": config.has_feature(Feature.FORMATTER),
            "has_linter": config.has_feature(Feature.LINTER),
            "has_vscode": config.has_feature(Feature.VSCODE),
            "has_license": config.has_feature(Feature.LICENSE),
            "has_makefile": config.has_feature(Feature.MAKEFILE),
            "has_editorconfig": config.has_feature(Feature.EDITORCONFIG),
            "has_git": config.has_feature(Feature.GIT),
        }

    def render_string(self, template_str: str, config: ProjectConfig) -> str:
        """Render a Jinja2 template string."""
        env = jinja2.Environment(
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True,
        )
        template = env.from_string(template_str)
        return template.render(**self._get_context(config))

    def render_template_dir(
        self,
        template_dir: Path,
        output_dir: Path,
        config: ProjectConfig,
    ) -> list[Path]:
        """Render all .j2 templates from a directory into the output directory."""
        context = self._get_context(config)
        created_files: list[Path] = []

        env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            undefined=jinja2.StrictUndefined,
            keep_trailing_newline=True,
        )

        for template_path in sorted(template_dir.rglob("*")):
            if template_path.is_dir():
                continue

            # Get relative path and apply name substitution
            rel_path = template_path.relative_to(template_dir)
            rel_str = str(rel_path)

            # Replace {{project_name}} in directory/file names
            rel_str = rel_str.replace("{{project_name}}", config.name)
            rel_str = rel_str.replace("{{project_name_safe}}", config.safe_name)

            # Remove .j2 extension
            if rel_str.endswith(".j2"):
                rel_str = rel_str[:-3]

            output_path = output_dir / rel_str

            # Render content
            try:
                template_rel = str(template_path.relative_to(template_dir))
                template = env.get_template(template_rel)
                content = template.render(**context)

                output_path.parent.mkdir(parents=True, exist_ok=True)
                output_path.write_text(content, encoding="utf-8")
                created_files.append(output_path)
                logger.debug("Rendered: %s", output_path)
            except Exception as e:
                logger.error("Failed to render %s: %s", template_path, e)

        return created_files

    def get_template_dir(self, config: ProjectConfig) -> Path | None:
        """Get the built-in template directory for a given config."""
        from bro.models.language import get_framework_info

        info = get_framework_info(config.language, config.framework)
        if info:
            template_dir = self.builtin_dir / info.template_dir
            if template_dir.exists():
                return template_dir
        return None
