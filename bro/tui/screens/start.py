"""TUI Start Screen — Multi-step project creation wizard."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    OptionList,
    Static,
)
from textual.widgets.option_list import Option

from bro.models.feature import DEFAULT_FEATURES, Feature
from bro.models.language import (
    Framework,
    Language,
    get_frameworks_for_language,
)
from bro.models.project import ProjectConfig


def create_contact_footer() -> Text:
    """Returns a styled Text object for the footer without string markup parsing."""
    t = Text(" If you find any issue, contact ", style="dim")
    t.append("Sameet Patro on LinkedIn", style="bold cyan link https://www.linkedin.com/in/sameet-patro/")
    return t


class LanguageStep(Screen[Language]):
    """Step 1: Select programming language."""

    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("\n[bold cyan]🚀 Select Language[/bold cyan]\n", classes="title-text"),
            Static("[dim]Choose the primary language for your project[/dim]\n", classes="subtitle-text"),
            OptionList(
                *[
                    Option(f"  {lang.icon}  {lang.display_name}", id=lang.value)
                    for lang in Language
                ],
                id="language-list",
            ),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id:
            self.dismiss(Language(event.option.id))

    def action_cancel(self) -> None:
        self.app.exit()


class FrameworkStep(Screen[Framework]):
    """Step 2: Select framework."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def __init__(self, language: Language) -> None:
        self.language = language
        super().__init__()

    def compose(self) -> ComposeResult:
        frameworks = get_frameworks_for_language(self.language)
        yield Header()
        yield Container(
            Static(
                f"\n[bold cyan]🛠️  Select Framework[/bold cyan]  [dim]({self.language.display_name})[/dim]\n",
                classes="title-text",
            ),
            OptionList(
                *[
                    Option(
                        f"  {fw.framework.display_name:<20} [dim]{fw.framework.description}[/dim]",
                        id=fw.framework.value,
                    )
                    for fw in frameworks
                ],
                id="framework-list",
            ),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id:
            self.dismiss(Framework(event.option.id))

    def action_back(self) -> None:
        self.dismiss(None)


class FeatureStep(Screen[list[Feature]]):
    """Step 3: Select features."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "confirm", "Confirm"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("\n[bold cyan]✨ Select Features[/bold cyan]\n", classes="title-text"),
            Static("[dim]Use Space to toggle, Enter to confirm[/dim]\n", classes="subtitle-text"),
            VerticalScroll(
                *[
                    Checkbox(
                        f"{fi.feature.icon}  {fi.feature.display_name}  [dim]{fi.feature.description}[/dim]",
                        value=fi.default_enabled,
                        id=f"feature-{fi.feature.value}",
                    )
                    for fi in DEFAULT_FEATURES
                ],
                id="feature-scroll",
            ),
            Horizontal(
                Button("← Back", variant="default", id="back-btn"),
                Button("Continue →", variant="primary", id="confirm-btn"),
                classes="nav-bar",
            ),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm-btn":
            self.action_confirm()
        elif event.button.id == "back-btn":
            self.action_back()

    def action_confirm(self) -> None:
        selected: list[Feature] = []
        for fi in DEFAULT_FEATURES:
            checkbox = self.query_one(f"#feature-{fi.feature.value}", Checkbox)
            if checkbox.value:
                selected.append(fi.feature)
        self.dismiss(selected)

    def action_back(self) -> None:
        self.dismiss(None)


class GitHubStep(Screen[tuple[bool, bool]]):
    """Step 4: GitHub repository options."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("\n[bold cyan]🐙 GitHub Repository[/bold cyan]\n", classes="title-text"),
            Static("[dim]Create a GitHub repository for this project?[/dim]\n", classes="subtitle-text"),
            OptionList(
                Option("  ✓  Yes, create a public repository", id="public"),
                Option("  🔒 Yes, create a private repository", id="private"),
                Option("  ✗  No, skip GitHub", id="skip"),
                id="github-list",
            ),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option.id == "skip":
            self.dismiss((False, False))
        elif event.option.id == "public":
            self.dismiss((True, False))
        else:
            self.dismiss((True, True))

    def action_back(self) -> None:
        self.dismiss(None)


class SummaryStep(Screen[bool]):
    """Step 5: Confirm and generate."""

    BINDINGS = [
        Binding("escape", "back", "Back"),
        Binding("enter", "confirm", "Generate"),
    ]

    def __init__(self, config: ProjectConfig) -> None:
        self.config = config
        super().__init__()

    def compose(self) -> ComposeResult:
        c = self.config
        features_str = ", ".join(f.display_name for f in c.features[:6])
        if len(c.features) > 6:
            features_str += f" +{len(c.features) - 6} more"

        yield Header()
        yield Container(
            Static("\n[bold cyan]📋 Project Summary[/bold cyan]\n", classes="title-text"),
            Vertical(
                Static(f"  [dim]Project:[/dim]    [bold]{c.name}[/bold]"),
                Static(f"  [dim]Language:[/dim]   [bold]{c.language.icon} {c.language.display_name}[/bold]"),
                Static(f"  [dim]Framework:[/dim]  [bold]{c.framework.display_name}[/bold]"),
                Static(f"  [dim]Features:[/dim]   {features_str}"),
                Static(f"  [dim]GitHub:[/dim]     {'🔒 Private' if c.github_private else '🌍 Public' if c.create_github_repo else '✗ No'}"),
                Static(f"  [dim]Path:[/dim]       [bold]{c.project_dir}[/bold]"),
                classes="summary-panel",
            ),
            Static(""),
            Horizontal(
                Button("← Back", variant="default", id="back-btn"),
                Button("🚀 Generate Project", variant="success", id="generate-btn"),
                classes="nav-bar",
            ),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "generate-btn":
            self.action_confirm()
        elif event.button.id == "back-btn":
            self.action_back()

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_back(self) -> None:
        self.dismiss(False)


class StartWizardApp(Screen[ProjectConfig | None]):
    """Complete start wizard flow managing all steps."""

    def __init__(self, project_name: str, output_dir: str | None = None) -> None:
        self.project_name = project_name
        self.output_dir = output_dir
        self._language: Language | None = None
        self._framework: Framework | None = None
        self._features: list[Feature] = []
        self._create_github: bool = False
        self._github_private: bool = True
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("\n[bold cyan]  Loading wizard...[/bold cyan]\n"),
            id="step-container",
        )
        yield Static(create_contact_footer(), classes="contact-footer")
        yield Footer()

    def on_mount(self) -> None:
        self._show_language_step()

    def _show_language_step(self) -> None:
        self.app.push_screen(LanguageStep(), callback=self._on_language_selected)

    def _on_language_selected(self, language: Language | None) -> None:
        if language is None:
            self.app.exit()
            return
        self._language = language
        self.app.push_screen(FrameworkStep(language), callback=self._on_framework_selected)

    def _on_framework_selected(self, framework: Framework | None) -> None:
        if framework is None:
            self._show_language_step()
            return
        self._framework = framework
        self.app.push_screen(FeatureStep(), callback=self._on_features_selected)

    def _on_features_selected(self, features: list[Feature] | None) -> None:
        if features is None:
            if self._language:
                self.app.push_screen(FrameworkStep(self._language), callback=self._on_framework_selected)
            return
        self._features = features
        self.app.push_screen(GitHubStep(), callback=self._on_github_selected)

    def _on_github_selected(self, result: tuple[bool, bool] | None) -> None:
        if result is None:
            self.app.push_screen(FeatureStep(), callback=self._on_features_selected)
            return
        self._create_github, self._github_private = result
        self._show_summary()

    def _show_summary(self) -> None:
        from pathlib import Path

        config = ProjectConfig(
            name=self.project_name,
            display_name=self.project_name.replace("-", " ").title(),
            language=self._language,  # type: ignore[arg-type]
            framework=self._framework,  # type: ignore[arg-type]
            features=self._features,
            create_github_repo=self._create_github,
            github_private=self._github_private,
            output_dir=Path(self.output_dir) if self.output_dir else Path.cwd(),
        )
        self.app.push_screen(SummaryStep(config), callback=lambda confirmed: self._on_confirmed(confirmed, config))

    def _on_confirmed(self, confirmed: bool, config: ProjectConfig) -> None:
        if not confirmed:
            self.app.push_screen(GitHubStep(), callback=self._on_github_selected)
            return
        self.dismiss(config)
