"""README generator — professional README.md with badges."""

from __future__ import annotations

from pathlib import Path

from bro.generators.base import BaseGenerator
from bro.models.feature import Feature
from bro.models.project import ProjectConfig
from bro.utils.fs import safe_write


class ReadmeGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "README"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.README)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        badges = []
        if config.has_feature(Feature.GITHUB_ACTIONS):
            badges.append(f"![CI](https://github.com/USERNAME/{config.name}/workflows/CI/badge.svg)")
        if config.has_feature(Feature.DOCKER):
            badges.append("![Docker](https://img.shields.io/badge/Docker-ready-blue)")
        if config.has_feature(Feature.LICENSE):
            badges.append("![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)")

        badge_line = " ".join(badges) + "\n\n" if badges else ""
        features_list = ""
        if config.has_feature(Feature.DOCKER):
            features_list += "- 🐳 Docker support\n"
        if config.has_feature(Feature.POSTGRESQL):
            features_list += "- 🐘 PostgreSQL database\n"
        if config.has_feature(Feature.REDIS):
            features_list += "- 🔴 Redis cache\n"
        if config.has_feature(Feature.JWT):
            features_list += "- 🔐 JWT authentication\n"
        if config.has_feature(Feature.SWAGGER):
            features_list += "- 📖 API documentation (Swagger)\n"
        if config.has_feature(Feature.TESTING):
            features_list += "- 🧪 Testing framework\n"
        if config.has_feature(Feature.GITHUB_ACTIONS):
            features_list += "- ⚡ CI/CD with GitHub Actions\n"

        content = f"""# {config.display_name or config.name}

{badge_line}> Built with [{config.language.display_name}]({config.framework.display_name}) — scaffolded by [Bro](https://github.com/sameetpatro/bro) 🚀

## About

A {config.framework.display_name} project.

## Features

{features_list if features_list else "- 🚀 Ready to develop\n"}
## Getting Started

### Prerequisites

- {config.language.display_name} installed
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

```bash
# Clone the repository
git clone https://github.com/USERNAME/{config.name}.git
cd {config.name}

# Install dependencies
{"uv sync" if config.language.value == "python" else "npm install" if config.language.value in ("javascript", "typescript", "react", "nextjs") else "go mod download" if config.language.value == "go" else "cargo build" if config.language.value == "rust" else "# See framework docs"}
```

### Running

```bash
{"uv run uvicorn app.main:app --reload" if config.framework.value == "fastapi" else "uv run python manage.py runserver" if config.framework.value == "django" else "uv run flask run --reload" if config.framework.value == "flask" else "go run ." if config.language.value == "go" else "npm run dev" if config.language.value in ("javascript", "typescript", "react", "nextjs") else "cargo run" if config.language.value == "rust" else "# See framework docs"}
```

{'''### Docker

```bash
docker compose up --build
```
''' if config.has_feature(Feature.DOCKER_COMPOSE) else ""}
## Project Structure

```
{config.name}/
├── README.md
{"├── pyproject.toml" if config.language.value == "python" else "├── package.json" if config.language.value in ("javascript", "typescript", "react", "nextjs") else "├── go.mod" if config.language.value == "go" else "├── Cargo.toml" if config.language.value == "rust" else "├── pom.xml"}
{"├── Dockerfile" if config.has_feature(Feature.DOCKER) else ""}
{"├── docker-compose.yml" if config.has_feature(Feature.DOCKER_COMPOSE) else ""}
└── ...
```

## License

{"This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details." if config.has_feature(Feature.LICENSE) else ""}

---

*Scaffolded with ❤️ by [Bro](https://github.com/sameetpatro/bro)*
"""
        path = project_dir / "README.md"
        safe_write(path, content)
        return [path]
