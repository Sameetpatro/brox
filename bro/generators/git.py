"""Git generator — git init, .gitignore, initial commit."""

from __future__ import annotations

from pathlib import Path

from bro.generators.base import BaseGenerator
from bro.models.feature import Feature
from bro.models.project import ProjectConfig
from bro.utils.fs import safe_write
from bro.utils.logger import get_logger
from bro.utils.process import run

logger = get_logger(__name__)

GITIGNORE_TEMPLATES: dict[str, str] = {
    "python": """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
dist/
build/
*.egg-info/
*.egg
.venv/
venv/
.env
.mypy_cache/
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
*.log
.DS_Store
""",
    "go": """# Go
*.exe
*.exe~
*.dll
*.so
*.dylib
*.test
*.out
vendor/
.env
*.log
.DS_Store
""",
    "javascript": """# Node.js
node_modules/
dist/
build/
.env
.env.local
*.log
npm-debug.log*
.DS_Store
coverage/
""",
    "typescript": """# TypeScript / Node.js
node_modules/
dist/
build/
.env
.env.local
*.log
npm-debug.log*
.DS_Store
coverage/
*.tsbuildinfo
""",
    "react": """# React
node_modules/
dist/
build/
.env
.env.local
*.log
npm-debug.log*
.DS_Store
coverage/
""",
    "nextjs": """# Next.js
node_modules/
.next/
out/
.env
.env.local
*.log
npm-debug.log*
.DS_Store
coverage/
""",
    "java": """# Java
*.class
*.jar
*.war
*.ear
target/
.idea/
*.iml
.env
*.log
.DS_Store
""",
    "kotlin": """# Kotlin
*.class
*.jar
build/
.gradle/
.idea/
*.iml
.env
*.log
.DS_Store
""",
    "rust": """# Rust
/target
Cargo.lock
*.pdb
.env
*.log
.DS_Store
""",
}


class GitGenerator(BaseGenerator):
    """Generates git initialization and .gitignore."""

    @property
    def name(self) -> str:
        return "Git"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.GIT)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        created: list[Path] = []

        # .gitignore
        gitignore = GITIGNORE_TEMPLATES.get(config.language.value, GITIGNORE_TEMPLATES["python"])
        gitignore_path = project_dir / ".gitignore"
        if safe_write(gitignore_path, gitignore):
            created.append(gitignore_path)

        # git init
        result = run("git init", cwd=project_dir)
        if result.success:
            logger.info("Git repository initialized")
        else:
            logger.warning("Failed to initialize git: %s", result.stderr)

        # Initial commit
        run("git add -A", cwd=project_dir)
        run('git commit -m "🎉 Initial commit — scaffolded with Bro"', cwd=project_dir)

        return created
