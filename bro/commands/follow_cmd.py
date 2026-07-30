"""bro follow — Learning mode: analyze a project's architecture."""

from __future__ import annotations

import time
from pathlib import Path

from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from bro.models.project import ProjectAnalysis
from bro.utils.console import console, print_banner, print_info, print_success
from bro.utils.fs import scan_directory
from bro.utils.logger import get_logger

logger = get_logger(__name__)

# ─── Detection heuristics ────────────────────────────────────────────────────

LANGUAGE_INDICATORS: dict[str, list[str]] = {
    "python": ["pyproject.toml", "setup.py", "requirements.txt", "Pipfile", "poetry.lock"],
    "go": ["go.mod", "go.sum"],
    "javascript": ["package.json"],
    "typescript": ["tsconfig.json"],
    "react": ["package.json"],  # + check for react dep
    "nextjs": ["next.config.js", "next.config.mjs", "next.config.ts"],
    "java": ["pom.xml", "build.gradle"],
    "kotlin": ["build.gradle.kts"],
    "rust": ["Cargo.toml"],
}

FRAMEWORK_INDICATORS: dict[str, list[str]] = {
    "fastapi": ["fastapi"],
    "django": ["django", "manage.py"],
    "flask": ["flask"],
    "gin": ["gin-gonic/gin"],
    "fiber": ["gofiber/fiber"],
    "echo": ["labstack/echo"],
    "express": ["express"],
    "nestjs": ["@nestjs/core"],
    "spring": ["spring-boot", "org.springframework"],
    "ktor": ["io.ktor"],
    "actix": ["actix-web"],
    "vite": ["vite"],
    "nextjs-react": ["next"],
}


def analyze_project(root: Path) -> ProjectAnalysis:
    """Analyze a project's architecture and technology stack."""
    analysis = ProjectAnalysis(root_path=root)

    # Scan directory structure
    analysis.directory_structure = scan_directory(root)

    # Detect config files
    for item in root.iterdir():
        if item.is_file():
            analysis.config_files.append(item.name)

    # Detect language
    for lang, indicators in LANGUAGE_INDICATORS.items():
        for indicator in indicators:
            if (root / indicator).exists():
                from bro.models.language import Language
                try:
                    analysis.language = Language(lang)
                except ValueError:
                    pass
                break

    # Detect features
    analysis.has_git = (root / ".git").exists()
    analysis.has_docker = (root / "Dockerfile").exists()
    analysis.has_docker_compose = (root / "docker-compose.yml").exists() or (root / "docker-compose.yaml").exists()
    analysis.has_readme = (root / "README.md").exists() or (root / "readme.md").exists()
    analysis.has_license = (root / "LICENSE").exists()
    analysis.has_makefile = (root / "Makefile").exists()
    analysis.has_editorconfig = (root / ".editorconfig").exists()
    analysis.has_env = (root / ".env").exists() or (root / ".env.example").exists()
    analysis.has_vscode = (root / ".vscode").exists()
    analysis.has_pre_commit = (root / ".pre-commit-config.yaml").exists()
    analysis.has_github_actions = (root / ".github" / "workflows").exists()

    # Read dependencies for framework detection
    _detect_framework_from_deps(root, analysis)

    return analysis


def _detect_framework_from_deps(root: Path, analysis: ProjectAnalysis) -> None:
    """Detect framework from dependency files."""
    dep_content = ""

    # Python
    if (root / "pyproject.toml").exists():
        dep_content = (root / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
    elif (root / "requirements.txt").exists():
        dep_content = (root / "requirements.txt").read_text(encoding="utf-8", errors="ignore")

    # Node
    if (root / "package.json").exists():
        dep_content += (root / "package.json").read_text(encoding="utf-8", errors="ignore")

    # Go
    if (root / "go.mod").exists():
        dep_content += (root / "go.mod").read_text(encoding="utf-8", errors="ignore")

    # Rust
    if (root / "Cargo.toml").exists():
        dep_content += (root / "Cargo.toml").read_text(encoding="utf-8", errors="ignore")

    dep_lower = dep_content.lower()

    for fw_name, indicators in FRAMEWORK_INDICATORS.items():
        for indicator in indicators:
            if indicator.lower() in dep_lower:
                from bro.models.language import Framework
                try:
                    analysis.framework = Framework(fw_name)
                except ValueError:
                    pass
                break

    # Detect services from deps/config
    if "postgresql" in dep_lower or "psycopg" in dep_lower or "postgres" in dep_lower:
        analysis.has_postgresql = True
    if "redis" in dep_lower or "ioredis" in dep_lower:
        analysis.has_redis = True
    if "jwt" in dep_lower or "jsonwebtoken" in dep_lower:
        analysis.has_jwt = True
    if "swagger" in dep_lower or "openapi" in dep_lower:
        analysis.has_swagger = True

    # Check for testing
    if "pytest" in dep_lower or "jest" in dep_lower or "testing" in dep_lower:
        analysis.has_testing = True
    # Check for linter
    if "ruff" in dep_lower or "eslint" in dep_lower or "golangci" in dep_lower:
        analysis.has_linter = True
    if "black" in dep_lower or "prettier" in dep_lower or "ruff" in dep_lower:
        analysis.has_formatter = True


def display_analysis(analysis: ProjectAnalysis) -> None:
    """Display a beautiful analysis of the project."""
    console.print()

    # Technology Stack
    table = Table(
        title="🔍 Project Analysis",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        padding=(0, 2),
    )
    table.add_column("Property", style="bold white", min_width=20)
    table.add_column("Value", min_width=30)

    table.add_row("Language", analysis.language.display_name if analysis.language else "[dim]Unknown[/dim]")
    table.add_row("Framework", analysis.framework.display_name if analysis.framework else "[dim]Unknown[/dim]")
    table.add_row("Package Manager", analysis.package_manager or "[dim]Unknown[/dim]")

    # Features
    features = []
    if analysis.has_git:
        features.append("🔀 Git")
    if analysis.has_docker:
        features.append("🐳 Docker")
    if analysis.has_docker_compose:
        features.append("🐳 Docker Compose")
    if analysis.has_postgresql:
        features.append("🐘 PostgreSQL")
    if analysis.has_redis:
        features.append("🔴 Redis")
    if analysis.has_jwt:
        features.append("🔐 JWT")
    if analysis.has_github_actions:
        features.append("⚡ GitHub Actions")
    if analysis.has_testing:
        features.append("🧪 Testing")
    if analysis.has_linter:
        features.append("🔍 Linter")
    if analysis.has_formatter:
        features.append("✨ Formatter")

    table.add_row("Features", ", ".join(features) if features else "[dim]None detected[/dim]")
    console.print(table)

    # Directory tree
    console.print()
    tree = Tree(f"📁 [bold]{analysis.root_path.name}[/bold]")
    for dir_path, files in sorted(analysis.directory_structure.items()):
        if dir_path == ".":
            branch = tree
        else:
            branch = tree.add(f"📁 {dir_path}")
        for f in files[:10]:  # Limit files shown
            branch.add(f"📄 {f}")
        if len(files) > 10:
            branch.add(f"[dim]... +{len(files) - 10} more files[/dim]")

    console.print(Panel(tree, title="[bold]Project Structure[/bold]", border_style="cyan"))


def run_follow() -> None:
    """Execute the follow command — learning mode."""
    print_banner()
    root = Path.cwd()

    print_info(f"Analyzing project at [bold]{root}[/bold]...")
    console.print()

    analysis = analyze_project(root)
    display_analysis(analysis)

    console.print()
    console.print("[bold cyan]👀 Watching project...[/bold cyan]")
    console.print("[dim]Make changes to your project. Press Ctrl+C when done.[/dim]")
    console.print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print()
        print_success("Learning session complete!")
        console.print("[dim]Run [bold]bro save <template_name>[/bold] to save as a template.[/dim]")
        console.print()

        # Re-analyze to capture changes
        final_analysis = analyze_project(root)
        # Store for bro save to pick up
        _store_analysis(final_analysis)


def _store_analysis(analysis: ProjectAnalysis) -> None:
    """Store the analysis for bro save to use."""
    import json

    from bro.config.defaults import BRO_HOME

    cache_file = BRO_HOME / ".last_analysis.json"
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(
        json.dumps(analysis.model_dump(mode="json"), indent=2, default=str),
        encoding="utf-8",
    )
