"""bro start command — Create a new project with interactive wizard or quick mode."""

from __future__ import annotations

from pathlib import Path

from bro.config.manager import get_config
from bro.generators.project import ProjectGenerator
from bro.models.project import ProjectConfig
from bro.utils.console import console, print_banner, print_error, print_info
from bro.utils.logger import get_logger
from bro.utils.platform import open_in_vscode

logger = get_logger(__name__)


def run_start(
    project_name: str,
    quick: bool = False,
    output_dir: str | None = None,
) -> None:
    """Execute the start command."""
    if quick:
        _run_quick(project_name, output_dir)
    else:
        _run_interactive(project_name, output_dir)


def _run_interactive(project_name: str, output_dir: str | None = None) -> None:
    """Run the full interactive TUI wizard."""
    from bro.tui.app import BroApp
    from bro.tui.screens.start import StartWizardApp

    class StartApp(BroApp):
        """App for the start wizard."""

        def on_mount(self) -> None:
            self.push_screen(
                StartWizardApp(project_name=project_name, output_dir=output_dir),
                callback=self._on_wizard_complete,
            )

        def _on_wizard_complete(self, config: ProjectConfig | None) -> None:
            self.exit(config)

    app = StartApp()
    config = app.run()

    if config is None:
        print_info("Project creation cancelled.")
        return

    # Generate the project
    generator = ProjectGenerator()
    try:
        project_dir = generator.generate(config)

        # GitHub repo creation
        if config.create_github_repo:
            _create_github_repo(config, project_dir)

        # Open in VS Code
        cfg = get_config()
        if cfg.open_vscode_after:
            open_in_vscode(str(project_dir))

    except FileExistsError:
        print_error(f"Directory '{config.name}' already exists.")
    except Exception as e:
        logger.exception("Project generation failed")
        print_error(f"Project generation failed: {e}")


def _run_quick(project_name: str, output_dir: str | None = None) -> None:
    """Run quick mode — use config defaults, only ask language & framework."""
    from bro.models.language import Language, get_frameworks_for_language

    print_banner()
    config = get_config()

    # Ask language
    console.print("\n[bold cyan]⚡ Quick Mode[/bold cyan]\n")

    languages = list(Language)
    for i, lang in enumerate(languages, 1):
        console.print(f"  {lang.icon} [{i}] {lang.display_name}")

    console.print()
    try:
        lang_choice = console.input("[bold]Language [/bold][dim](number)[/dim]: ")
        lang_idx = int(lang_choice) - 1
        if lang_idx < 0 or lang_idx >= len(languages):
            print_error("Invalid choice.")
            return
        language = languages[lang_idx]
    except (ValueError, KeyboardInterrupt):
        print_info("Cancelled.")
        return

    # Ask framework
    frameworks = get_frameworks_for_language(language)
    console.print()
    for i, fw in enumerate(frameworks, 1):
        console.print(f"  [{i}] {fw.framework.display_name}")

    console.print()
    try:
        fw_choice = console.input("[bold]Framework [/bold][dim](number)[/dim]: ")
        fw_idx = int(fw_choice) - 1
        if fw_idx < 0 or fw_idx >= len(frameworks):
            print_error("Invalid choice.")
            return
        framework = frameworks[fw_idx].framework
    except (ValueError, KeyboardInterrupt):
        print_info("Cancelled.")
        return

    # Build config from defaults
    project_config = ProjectConfig(
        name=project_name,
        display_name=project_name.replace("-", " ").title(),
        language=language,
        framework=framework,
        features=config.get_quick_features(),
        output_dir=Path(output_dir) if output_dir else Path.cwd(),
    )

    console.print()
    generator = ProjectGenerator()
    try:
        generator.generate(project_config)
    except Exception as e:
        logger.exception("Quick project generation failed")
        print_error(f"Generation failed: {e}")


def _create_github_repo(config: ProjectConfig, project_dir: Path) -> None:
    """Create GitHub repository and push."""
    try:
        from bro.github.auth import ensure_authenticated
        from bro.github.repo import create_and_push

        token = ensure_authenticated()
        if token:
            create_and_push(
                token=token,
                repo_name=config.name,
                project_dir=project_dir,
                private=config.github_private,
            )
    except ImportError:
        logger.warning("GitHub module not available")
    except Exception as e:
        logger.error("GitHub repo creation failed: %s", e)
        print_error(f"GitHub repo creation failed: {e}")
