"""bro use — Create a project from a saved template."""

from __future__ import annotations

from pathlib import Path

import yaml

from bro.config.defaults import TEMPLATES_DIR
from bro.models.project import ProjectConfig
from bro.models.template import TemplateConfig
from bro.templates.renderer import TemplateRenderer
from bro.utils.console import console, print_banner, print_error, print_info, print_success
from bro.utils.logger import get_logger

logger = get_logger(__name__)


def _list_templates() -> list[tuple[str, TemplateConfig]]:
    """List all saved user templates."""
    templates: list[tuple[str, TemplateConfig]] = []
    if not TEMPLATES_DIR.exists():
        return templates

    for template_dir in sorted(TEMPLATES_DIR.iterdir()):
        if template_dir.is_dir():
            config_file = template_dir / "template.yaml"
            if config_file.exists():
                try:
                    data = yaml.safe_load(config_file.read_text(encoding="utf-8"))
                    config = TemplateConfig(**data)
                    templates.append((template_dir.name, config))
                except Exception as e:
                    logger.warning("Failed to load template %s: %s", template_dir.name, e)
    return templates


def run_use() -> None:
    """Browse and use a saved template."""
    print_banner()

    templates = _list_templates()
    if not templates:
        print_info("No saved templates found.")
        print_info("Use [bold]bro save <name>[/bold] to save a template first.")
        return

    console.print("\n[bold cyan]📦 Saved Templates[/bold cyan]\n")
    for i, (name, config) in enumerate(templates, 1):
        lang_str = f"[{config.language.display_name}]" if config.language else ""
        fw_str = f"({config.framework.display_name})" if config.framework else ""
        console.print(f"  [{i}] [bold]{name}[/bold] {lang_str} {fw_str}")
        if config.description:
            console.print(f"      [dim]{config.description}[/dim]")

    console.print()
    try:
        choice = console.input("[bold]Select template [/bold][dim](number)[/dim]: ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(templates):
            print_error("Invalid choice.")
            return
    except (ValueError, KeyboardInterrupt):
        print_info("Cancelled.")
        return

    name, config = templates[idx]

    # Ask project name
    console.print()
    try:
        project_name = console.input("[bold]Project name: [/bold]")
        if not project_name.strip():
            print_error("Project name cannot be empty.")
            return
    except KeyboardInterrupt:
        print_info("Cancelled.")
        return

    project_name = project_name.strip()
    output_dir = Path.cwd() / project_name

    if output_dir.exists():
        print_error(f"Directory '{project_name}' already exists.")
        return

    # Render template
    template_dir = TEMPLATES_DIR / name
    renderer = TemplateRenderer()

    # Create a minimal ProjectConfig for rendering
    project_config = ProjectConfig(
        name=project_name,
        display_name=project_name.replace("-", " ").title(),
        language=config.language or "python",
        framework=config.framework or "fastapi",
        features=[],
    )

    created = renderer.render_template_dir(template_dir, output_dir, project_config)

    # Rename .j2 files if any slipped through
    for f in output_dir.rglob("*.j2"):
        f.rename(f.with_suffix(""))

    console.print()
    print_success(f"Project [bold]{project_name}[/bold] created from template [bold]{name}[/bold]!")
    print_info(f"  📁 {output_dir}")
    print_info(f"  📦 {len(created)} files generated")
    console.print()
