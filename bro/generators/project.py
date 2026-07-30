"""Project generator — orchestrates all sub-generators to create a complete project."""

from __future__ import annotations

from pathlib import Path

from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn

from bro.generators.base import BaseGenerator
from bro.generators.docker import DockerComposeGenerator, DockerGenerator
from bro.generators.extras import (
    CIGenerator,
    EditorConfigGenerator,
    EnvGenerator,
    LicenseGenerator,
    MakefileGenerator,
    PreCommitGenerator,
    VSCodeGenerator,
)
from bro.generators.git import GitGenerator
from bro.generators.readme import ReadmeGenerator
from bro.models.project import ProjectConfig
from bro.templates.renderer import TemplateRenderer
from bro.utils.console import console, print_error, print_info, print_success
from bro.utils.fs import ensure_dir
from bro.utils.logger import get_logger
from bro.utils.process import run

logger = get_logger(__name__)


class ProjectGenerator:
    """Orchestrates project generation from config."""

    def __init__(self) -> None:
        self.renderer = TemplateRenderer()
        self.generators: list[BaseGenerator] = [
            # Order matters — git should be last so it captures all files
            DockerGenerator(),
            DockerComposeGenerator(),
            ReadmeGenerator(),
            LicenseGenerator(),
            EnvGenerator(),
            EditorConfigGenerator(),
            VSCodeGenerator(),
            MakefileGenerator(),
            PreCommitGenerator(),
            CIGenerator(),
            GitGenerator(),  # Git last — captures everything in initial commit
        ]

    def generate(self, config: ProjectConfig) -> Path:
        """Generate a complete project from the given config."""
        project_dir = config.project_dir

        if project_dir.exists():
            print_error(f"Directory already exists: {project_dir}")
            raise FileExistsError(f"Directory already exists: {project_dir}")

        ensure_dir(project_dir)
        print_info(f"Creating project at [bold]{project_dir}[/bold]")

        all_created: list[Path] = []

        with Progress(
            SpinnerColumn(style="cyan"),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30, complete_style="cyan", finished_style="green"),
            TextColumn("[dim]{task.fields[status]}"),
            console=console,
            transient=False,
        ) as progress:
            # Step 1: Render framework template
            task = progress.add_task(
                "Rendering template...",
                total=len(self.generators) + 2,
                status="",
            )

            template_dir = self.renderer.get_template_dir(config)
            if template_dir:
                created = self.renderer.render_template_dir(template_dir, project_dir, config)
                all_created.extend(created)
                progress.update(task, advance=1, status=f"{len(created)} files")
            else:
                # No built-in template — create minimal structure
                self._create_minimal_structure(config, project_dir)
                progress.update(task, advance=1, status="minimal")

            # Step 2: Install dependencies
            progress.update(task, description="Installing dependencies...", status="")
            self._install_dependencies(config, project_dir)
            progress.update(task, advance=1, status="done")

            # Step 3: Run generators
            for generator in self.generators:
                if generator.should_run(config):
                    progress.update(
                        task,
                        description=f"Generating {generator.name}...",
                        status="",
                    )
                    try:
                        created = generator.generate(config, project_dir)
                        all_created.extend(created)
                        progress.update(task, advance=1, status="✓")
                    except Exception as e:
                        logger.error("Generator %s failed: %s", generator.name, e)
                        progress.update(task, advance=1, status="✗")
                else:
                    progress.update(task, advance=1, status="skip")

        console.print()
        print_success(f"Project [bold]{config.name}[/bold] created successfully! 🎉")
        print_info(f"  📁 {project_dir}")
        print_info(f"  📦 {len(all_created)} files generated")
        print_info(f"  🛠️  {config.language.display_name} / {config.framework.display_name}")
        console.print()

        return project_dir

    def _install_dependencies(self, config: ProjectConfig, project_dir: Path) -> None:
        """Install dependencies based on language."""
        lang = config.language.value

        if lang == "python":
            # Check if pyproject.toml exists
            if (project_dir / "pyproject.toml").exists():
                result = run("uv sync", cwd=project_dir, timeout=120)
                if not result.success:
                    logger.warning("Failed to install Python deps: %s", result.stderr)
        elif lang in ("javascript", "typescript", "react", "nextjs"):
            if (project_dir / "package.json").exists():
                result = run("npm install", cwd=project_dir, timeout=120)
                if not result.success:
                    logger.warning("Failed to install Node deps: %s", result.stderr)
        elif lang == "go":
            if (project_dir / "go.mod").exists():
                result = run("go mod tidy", cwd=project_dir, timeout=60)
                if not result.success:
                    logger.warning("Failed to tidy Go modules: %s", result.stderr)
        elif lang == "rust":
            if (project_dir / "Cargo.toml").exists():
                result = run("cargo check", cwd=project_dir, timeout=120)
                if not result.success:
                    logger.warning("Failed to check Rust project: %s", result.stderr)

    def _create_minimal_structure(self, config: ProjectConfig, project_dir: Path) -> None:
        """Create a minimal project structure when no template exists."""
        lang = config.language.value
        name = config.safe_name

        if lang == "python":
            (project_dir / name).mkdir(exist_ok=True)
            (project_dir / name / "__init__.py").write_text(f'"""{ config.display_name or config.name }."""\n')
            (project_dir / "pyproject.toml").write_text(
                f'[project]\nname = "{config.name}"\nversion = "0.1.0"\nrequires-python = ">=3.12"\ndependencies = []\n\n[build-system]\nrequires = ["hatchling"]\nbuild-backend = "hatchling.build"\n'
            )
        elif lang in ("javascript", "typescript"):
            (project_dir / "src").mkdir(exist_ok=True)
            (project_dir / "package.json").write_text(
                f'{{"name": "{config.name}", "version": "0.1.0", "scripts": {{"dev": "echo \\"Configure dev script\\""}}}}\n'
            )
        elif lang == "go":
            (project_dir / "go.mod").write_text(f"module {config.name}\n\ngo 1.22\n")
            (project_dir / "main.go").write_text('package main\n\nimport "fmt"\n\nfunc main() {\n\tfmt.Println("Hello from ' + config.name + '")\n}\n')
