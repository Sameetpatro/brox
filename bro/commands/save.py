"""bro save — Save current project as a reusable template."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

from bro.config.defaults import DEFAULT_IGNORE_PATTERNS, TEMPLATES_DIR
from bro.models.template import TemplateConfig
from bro.utils.console import console, print_banner, print_info, print_success
from bro.utils.logger import get_logger

logger = get_logger(__name__)


def run_save(template_name: str) -> None:
    """Save the current directory as a template."""
    print_banner()

    root = Path.cwd()
    project_name = root.name

    print_info(f"Saving [bold]{root}[/bold] as template [bold]{template_name}[/bold]...")

    # Create template config
    config = TemplateConfig(
        name=template_name,
        description=f"Template created from {project_name}",
        source_path=str(root),
        placeholders={project_name: "{{project_name}}"},
    )

    # Try to detect language/framework from last analysis
    _enrich_from_analysis(config)

    # Create template directory
    template_dir = TEMPLATES_DIR / template_name
    if template_dir.exists():
        console.print(f"[yellow]Template '{template_name}' already exists. Overwrite? (y/n)[/yellow]")
        try:
            answer = console.input("> ")
            if answer.lower() != "y":
                print_info("Cancelled.")
                return
            shutil.rmtree(template_dir)
        except KeyboardInterrupt:
            return

    template_dir.mkdir(parents=True, exist_ok=True)

    # Copy files, applying ignore patterns and creating Jinja2 templates
    file_count = 0
    for item in _walk_project(root, DEFAULT_IGNORE_PATTERNS):
        rel_path = item.relative_to(root)

        # Replace project name in path
        rel_str = str(rel_path).replace(project_name, "{{project_name}}")

        dest = template_dir / rel_str
        dest.parent.mkdir(parents=True, exist_ok=True)

        try:
            content = item.read_text(encoding="utf-8")
            # Replace project name in content
            content = content.replace(project_name, "{{project_name}}")
            # Save as .j2 template
            dest_j2 = Path(str(dest) + ".j2")
            dest_j2.write_text(content, encoding="utf-8")
            file_count += 1
        except (UnicodeDecodeError, PermissionError):
            # Binary file — copy as-is
            shutil.copy2(item, dest)
            file_count += 1

    # Save template config
    config_path = template_dir / "template.yaml"
    config_path.write_text(
        yaml.dump(config.model_dump(mode="json"), default_flow_style=False, sort_keys=False),
        encoding="utf-8",
    )

    console.print()
    print_success(f"Template [bold]{template_name}[/bold] saved! ({file_count} files)")
    print_info(f"  📁 {template_dir}")
    print_info("  Run [bold]bro use[/bold] to create a project from this template.")
    console.print()


def _walk_project(root: Path, ignore_patterns: list[str]) -> list[Path]:
    """Walk project tree, ignoring specified patterns."""
    files: list[Path] = []

    def _should_ignore(path: Path) -> bool:
        name = path.name
        for pattern in ignore_patterns:
            if pattern.startswith("*"):
                if name.endswith(pattern[1:]):
                    return True
            elif name == pattern:
                return True
        return False

    for item in sorted(root.rglob("*")):
        if item.is_file() and not any(_should_ignore(p) for p in item.relative_to(root).parents) and not _should_ignore(item):
            files.append(item)

    return files


def _enrich_from_analysis(config: TemplateConfig) -> None:
    """Enrich template config from cached analysis."""
    import json

    from bro.config.defaults import BRO_HOME

    cache_file = BRO_HOME / ".last_analysis.json"
    if cache_file.exists():
        try:
            data = json.loads(cache_file.read_text(encoding="utf-8"))
            if data.get("language"):
                from bro.models.language import Language
                config.language = Language(data["language"])
            if data.get("framework"):
                from bro.models.language import Framework
                config.framework = Framework(data["framework"])
        except Exception:
            pass
