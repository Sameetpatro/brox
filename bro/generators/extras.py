"""License, .env, EditorConfig, VS Code, Makefile, pre-commit, CI generators."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from bro.generators.base import BaseGenerator
from bro.models.feature import Feature
from bro.models.project import ProjectConfig
from bro.utils.fs import safe_write


class LicenseGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "License"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.LICENSE)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        year = datetime.now().year
        content = f"""MIT License

Copyright (c) {year} {config.display_name or config.name}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
        path = project_dir / "LICENSE"
        safe_write(path, content)
        return [path]


class EnvGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return ".env"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.DOTENV)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        lines = [
            f"# {config.name} Environment Variables",
            f"APP_NAME={config.name}",
            "APP_ENV=development",
            "APP_DEBUG=true",
            "APP_PORT=8000",
            "",
        ]
        if config.has_feature(Feature.POSTGRESQL):
            lines += [
                "# Database",
                f"DATABASE_URL=postgresql://postgres:postgres@localhost:5432/{config.safe_name}",
                "DB_HOST=localhost",
                "DB_PORT=5432",
                f"DB_NAME={config.safe_name}",
                "DB_USER=postgres",
                "DB_PASSWORD=postgres",
                "",
            ]
        if config.has_feature(Feature.REDIS):
            lines += [
                "# Redis",
                "REDIS_URL=redis://localhost:6379/0",
                "REDIS_HOST=localhost",
                "REDIS_PORT=6379",
                "",
            ]
        if config.has_feature(Feature.JWT):
            lines += [
                "# JWT",
                "JWT_SECRET_KEY=your-secret-key-change-in-production",
                "JWT_ALGORITHM=HS256",
                "JWT_EXPIRATION_MINUTES=30",
                "",
            ]

        created: list[Path] = []
        env_path = project_dir / ".env"
        safe_write(env_path, "\n".join(lines))
        created.append(env_path)

        example_path = project_dir / ".env.example"
        # Replace values with placeholders
        example_lines = [line.split("=")[0] + "=" if "=" in line and not line.startswith("#") else line for line in lines]
        safe_write(example_path, "\n".join(example_lines))
        created.append(example_path)
        return created


class EditorConfigGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "EditorConfig"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.EDITORCONFIG)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        indent = "space"
        size = "4" if config.language.value in ("python", "java", "kotlin", "rust") else "2"
        content = f"""root = true

[*]
indent_style = {indent}
indent_size = {size}
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false

[Makefile]
indent_style = tab
"""
        path = project_dir / ".editorconfig"
        safe_write(path, content)
        return [path]


class VSCodeGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "VS Code Settings"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.VSCODE)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        created: list[Path] = []
        vscode_dir = project_dir / ".vscode"

        settings = '{\n  "editor.formatOnSave": true,\n  "editor.defaultFormatter": null,\n'
        if config.language.value == "python":
            settings += '  "[python]": {\n    "editor.defaultFormatter": "charliermarsh.ruff"\n  },\n'
            settings += '  "python.analysis.typeCheckingMode": "basic",\n'
        elif config.language.value in ("javascript", "typescript", "react", "nextjs"):
            settings += '  "[javascript]": {\n    "editor.defaultFormatter": "esbenp.prettier-vscode"\n  },\n'
            settings += '  "[typescript]": {\n    "editor.defaultFormatter": "esbenp.prettier-vscode"\n  },\n'
        settings += '  "files.trimTrailingWhitespace": true,\n  "files.insertFinalNewline": true\n}\n'
        settings_path = vscode_dir / "settings.json"
        safe_write(settings_path, settings)
        created.append(settings_path)

        extensions: list[str] = []
        if config.language.value == "python":
            extensions = ["ms-python.python", "charliermarsh.ruff", "ms-python.mypy-type-checker"]
        elif config.language.value in ("javascript", "typescript", "react", "nextjs"):
            extensions = ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"]
        elif config.language.value == "go":
            extensions = ["golang.go"]
        elif config.language.value == "rust":
            extensions = ["rust-lang.rust-analyzer"]
        elif config.language.value == "java":
            extensions = ["vscjava.vscode-java-pack"]

        if config.has_feature(Feature.DOCKER):
            extensions.append("ms-azuretools.vscode-docker")

        if extensions:
            ext_content = '{\n  "recommendations": [\n'
            ext_content += ",\n".join(f'    "{e}"' for e in extensions)
            ext_content += "\n  ]\n}\n"
            ext_path = vscode_dir / "extensions.json"
            safe_write(ext_path, ext_content)
            created.append(ext_path)

        return created


class MakefileGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "Makefile"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.MAKEFILE)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        targets = ".PHONY: help dev test lint format clean\n\nhelp: ## Show help\n\t@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = \":.*?## \"}; {printf \"\\033[36m%-20s\\033[0m %s\\n\", $$1, $$2}'\n\n"

        if config.language.value == "python":
            targets += "dev: ## Run development server\n\tuv run uvicorn app.main:app --reload\n\n"
            targets += "test: ## Run tests\n\tuv run pytest\n\n"
            targets += "lint: ## Run linter\n\tuv run ruff check .\n\n"
            targets += "format: ## Format code\n\tuv run ruff format .\n\n"
            targets += "clean: ## Clean artifacts\n\trm -rf __pycache__ .pytest_cache .ruff_cache .mypy_cache dist build\n\n"
        elif config.language.value == "go":
            targets += "dev: ## Run development server\n\tgo run .\n\n"
            targets += "test: ## Run tests\n\tgo test ./...\n\n"
            targets += "build: ## Build binary\n\tgo build -o bin/server .\n\n"
            targets += "clean: ## Clean artifacts\n\trm -rf bin/\n\n"
        elif config.language.value in ("javascript", "typescript", "react", "nextjs"):
            targets += "dev: ## Run development server\n\tnpm run dev\n\n"
            targets += "test: ## Run tests\n\tnpm test\n\n"
            targets += "build: ## Build project\n\tnpm run build\n\n"
            targets += "lint: ## Run linter\n\tnpm run lint\n\n"
            targets += "clean: ## Clean artifacts\n\trm -rf node_modules dist build\n\n"
        else:
            targets += "dev: ## Run development server\n\techo 'Not configured'\n\n"

        if config.has_feature(Feature.DOCKER):
            targets += "docker-build: ## Build Docker image\n\tdocker build -t $(shell basename $(CURDIR)) .\n\n"
        if config.has_feature(Feature.DOCKER_COMPOSE):
            targets += "up: ## Start services\n\tdocker compose up -d\n\ndown: ## Stop services\n\tdocker compose down\n\n"

        path = project_dir / "Makefile"
        safe_write(path, targets)
        return [path]


class PreCommitGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "Pre-commit Hooks"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.PRE_COMMIT)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        hooks = "repos:\n  - repo: https://github.com/pre-commit/pre-commit-hooks\n    rev: v4.6.0\n    hooks:\n      - id: trailing-whitespace\n      - id: end-of-file-fixer\n      - id: check-yaml\n      - id: check-added-large-files\n"
        if config.language.value == "python":
            hooks += "\n  - repo: https://github.com/astral-sh/ruff-pre-commit\n    rev: v0.5.0\n    hooks:\n      - id: ruff\n        args: [--fix]\n      - id: ruff-format\n"
        path = project_dir / ".pre-commit-config.yaml"
        safe_write(path, hooks)
        return [path]


class CIGenerator(BaseGenerator):
    @property
    def name(self) -> str:
        return "GitHub Actions"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.GITHUB_ACTIONS)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        if config.language.value == "python":
            content = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v3
      - run: uv sync
      - run: uv run ruff check .
      - run: uv run pytest --cov
"""
        elif config.language.value == "go":
            content = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go test ./...
      - run: go vet ./...
"""
        elif config.language.value in ("javascript", "typescript", "react", "nextjs"):
            content = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
      - run: npm ci
      - run: npm run lint
      - run: npm test
"""
        else:
            content = """name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: echo "Add your CI steps here"
"""
        ci_dir = project_dir / ".github" / "workflows"
        path = ci_dir / "ci.yml"
        safe_write(path, content)
        return [path]
