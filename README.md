# 🚀 Bro — Developer Workspace Manager

![CI](https://github.com/sameetpatro/bro/workflows/CI/badge.svg)
![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-macOS%20%7C%20Linux%20%7C%20Windows-lightgrey)

> The fastest and smartest way for developers to create projects, save templates, learn project structures, clone repositories, and use AI to automate development tasks.

---

## ✨ Features

| Command | Description |
|---------|-------------|
| `bro start <name>` | Create a new project with an interactive TUI wizard |
| `bro start --quick <name>` | Quick mode — only ask language & framework |
| `bro follow` | Learning mode — analyze project architecture |
| `bro save <name>` | Save current project as a reusable template |
| `bro use` | Create a project from a saved template |
| `bro delete` | Delete a saved template |
| `bro clone` | Clone a repo with analysis and post-clone options |
| `bro check` | Check installed development tools |
| `bro config` | View and edit Bro configuration |
| `bro ai` | AI-powered development assistant |
| `bro update` | Update Bro and templates |

## 🛠️ Supported Languages & Frameworks

| Language | Frameworks |
|----------|-----------|
| 🐍 Python | FastAPI, Django, Flask |
| 🔵 Go | Gin, Fiber, Echo |
| 🟨 JavaScript | Express, NestJS |
| 🔷 TypeScript | Express, NestJS |
| ⚛️ React | Vite, Next.js |
| ▲ Next.js | App Router |
| ☕ Java | Spring Boot |
| 🟣 Kotlin | Ktor |
| 🦀 Rust | Actix Web |

## 📦 Installation

```bash
# With pipx (recommended)
pipx install bro

# With pip
pip install bro

# From source
git clone https://github.com/sameetpatro/bro.git
cd bro
uv sync
uv run bro --help
```

## 🚀 Quick Start

```bash
# Create a new FastAPI project
bro start my-api

# Quick mode (uses defaults)
bro start --quick my-api

# Check your dev environment
bro check

# Learn a project's structure
cd existing-project
bro follow
bro save my-template

# Use a saved template
bro use

# AI-powered project creation
bro ai
```

## ⚙️ Configuration

Bro stores configuration in `~/.bro/config.yaml`:

```yaml
default_language: python
default_framework: fastapi
always_git: true
always_docker: false
always_testing: true
always_linter: true
```

Edit interactively with `bro config`.

## 🏗️ Architecture

```
bro/
├── cli/          # Typer CLI entry point
├── tui/          # Textual TUI screens & widgets
├── ai/           # LLM client & prompts
├── templates/    # Jinja2 templates & registry
├── generators/   # Project component generators
├── config/       # YAML configuration management
├── github/       # Device flow auth & repo creation
├── clone/        # Repository cloning & analysis
├── follow/       # Project learning & template extraction
├── commands/     # One module per command
├── models/       # Pydantic data models
└── utils/        # Cross-platform helpers
```

## 🤖 AI Features

Bro AI requires an API key:

```bash
bro config
# Set ai_api_key to your OpenAI API key
```

- **Build Something**: Describe what you want, AI generates the project plan
- **Debug Project**: Paste errors, AI diagnoses and suggests fixes
- **Improve Project**: AI analyzes your project and suggests improvements

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with ❤️ using [Typer](https://typer.tiangolo.com/), [Textual](https://textual.textualize.io/), and [Jinja2](https://jinja.palletsprojects.com/)*
