"""Language and framework definitions — the registry of all supported stacks."""

from __future__ import annotations

from enum import Enum
from typing import ClassVar

from pydantic import BaseModel


class Language(str, Enum):
    """Supported programming languages."""

    PYTHON = "python"
    GO = "go"
    JAVA = "java"
    KOTLIN = "kotlin"
    RUST = "rust"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    NEXTJS = "nextjs"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names: dict[str, str] = {
            "python": "Python",
            "go": "Go",
            "java": "Java",
            "kotlin": "Kotlin",
            "rust": "Rust",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "react": "React",
            "nextjs": "Next.js",
        }
        return names.get(self.value, self.value.title())

    @property
    def icon(self) -> str:
        """Emoji icon for terminal display."""
        icons: dict[str, str] = {
            "python": "🐍",
            "go": "🔵",
            "java": "☕",
            "kotlin": "🟣",
            "rust": "🦀",
            "javascript": "🟨",
            "typescript": "🔷",
            "react": "⚛️",
            "nextjs": "▲",
        }
        return icons.get(self.value, "📦")

    @property
    def color(self) -> str:
        """Rich color for TUI display."""
        colors: dict[str, str] = {
            "python": "#3776AB",
            "go": "#00ADD8",
            "java": "#ED8B00",
            "kotlin": "#7F52FF",
            "rust": "#DEA584",
            "javascript": "#F7DF1E",
            "typescript": "#3178C6",
            "react": "#61DAFB",
            "nextjs": "#FFFFFF",
        }
        return colors.get(self.value, "#AAAAAA")


class Framework(str, Enum):
    """Supported frameworks, organized by language."""

    # Python
    FASTAPI = "fastapi"
    DJANGO = "django"
    FLASK = "flask"

    # Go
    GIN = "gin"
    FIBER = "fiber"
    ECHO = "echo"

    # JavaScript / TypeScript
    EXPRESS = "express"
    NESTJS = "nestjs"

    # React
    VITE = "vite"
    NEXTJS_REACT = "nextjs-react"

    # Java
    SPRING = "spring"

    # Kotlin
    KTOR = "ktor"

    # Rust
    ACTIX = "actix"

    # Next.js (standalone)
    NEXTJS_DEFAULT = "nextjs-default"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        names: dict[str, str] = {
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "gin": "Gin",
            "fiber": "Fiber",
            "echo": "Echo",
            "express": "Express",
            "nestjs": "NestJS",
            "vite": "Vite + React",
            "nextjs-react": "Next.js",
            "spring": "Spring Boot",
            "ktor": "Ktor",
            "actix": "Actix Web",
            "nextjs-default": "Next.js (App Router)",
        }
        return names.get(self.value, self.value.title())

    @property
    def description(self) -> str:
        """Short description for TUI display."""
        descriptions: dict[str, str] = {
            "fastapi": "Modern, fast web framework for building APIs",
            "django": "High-level Python web framework with batteries included",
            "flask": "Lightweight WSGI micro web framework",
            "gin": "HTTP web framework with martini-like API",
            "fiber": "Express-inspired Go web framework built on Fasthttp",
            "echo": "High performance, minimalist Go web framework",
            "express": "Fast, unopinionated, minimalist web framework for Node.js",
            "nestjs": "Progressive Node.js framework for enterprise apps",
            "vite": "Next-generation frontend tooling with React",
            "nextjs-react": "The React framework for full-stack web applications",
            "spring": "Java-based enterprise application framework",
            "ktor": "Asynchronous web framework for Kotlin",
            "actix": "Powerful, pragmatic, and extremely fast web framework for Rust",
            "nextjs-default": "Full-stack React framework with App Router",
        }
        return descriptions.get(self.value, "")


class FrameworkInfo(BaseModel):
    """Metadata about a framework including its parent language."""

    framework: Framework
    language: Language
    template_dir: str  # Relative path under templates/builtin/
    package_manager: str  # e.g., "uv", "go", "npm", "cargo"
    dev_command: str  # e.g., "uv run uvicorn main:app --reload"

    # Class-level registry
    _registry: ClassVar[dict[Framework, FrameworkInfo]] = {}

    @classmethod
    def register(cls, info: FrameworkInfo) -> None:
        """Register a framework in the global registry."""
        cls._registry[info.framework] = info

    @classmethod
    def get(cls, framework: Framework) -> FrameworkInfo:
        """Get framework info from the registry."""
        return cls._registry[framework]

    @classmethod
    def get_frameworks_for_language(cls, language: Language) -> list[FrameworkInfo]:
        """Get all frameworks available for a given language."""
        return [info for info in cls._registry.values() if info.language == language]


# ─── Registry Population ─────────────────────────────────────────────────────

_FRAMEWORK_DEFINITIONS: list[dict[str, str]] = [
    # Python
    {"framework": "fastapi", "language": "python", "template_dir": "python/fastapi", "package_manager": "uv", "dev_command": "uv run uvicorn app.main:app --reload"},
    {"framework": "django", "language": "python", "template_dir": "python/django", "package_manager": "uv", "dev_command": "uv run python manage.py runserver"},
    {"framework": "flask", "language": "python", "template_dir": "python/flask", "package_manager": "uv", "dev_command": "uv run flask run --reload"},
    # Go
    {"framework": "gin", "language": "go", "template_dir": "go/gin", "package_manager": "go", "dev_command": "go run ."},
    {"framework": "fiber", "language": "go", "template_dir": "go/fiber", "package_manager": "go", "dev_command": "go run ."},
    {"framework": "echo", "language": "go", "template_dir": "go/echo", "package_manager": "go", "dev_command": "go run ."},
    # JavaScript
    {"framework": "express", "language": "javascript", "template_dir": "javascript/express", "package_manager": "npm", "dev_command": "npm run dev"},
    {"framework": "nestjs", "language": "javascript", "template_dir": "javascript/nestjs", "package_manager": "npm", "dev_command": "npm run start:dev"},
    # TypeScript (shares express/nestjs templates but with TS config)
    {"framework": "express", "language": "typescript", "template_dir": "typescript/express", "package_manager": "npm", "dev_command": "npm run dev"},
    {"framework": "nestjs", "language": "typescript", "template_dir": "typescript/nestjs", "package_manager": "npm", "dev_command": "npm run start:dev"},
    # React
    {"framework": "vite", "language": "react", "template_dir": "react/vite", "package_manager": "npm", "dev_command": "npm run dev"},
    {"framework": "nextjs-react", "language": "react", "template_dir": "react/nextjs", "package_manager": "npm", "dev_command": "npm run dev"},
    # Java
    {"framework": "spring", "language": "java", "template_dir": "java/spring", "package_manager": "maven", "dev_command": "./mvnw spring-boot:run"},
    # Kotlin
    {"framework": "ktor", "language": "kotlin", "template_dir": "kotlin/ktor", "package_manager": "gradle", "dev_command": "./gradlew run"},
    # Rust
    {"framework": "actix", "language": "rust", "template_dir": "rust/actix", "package_manager": "cargo", "dev_command": "cargo run"},
    # Next.js standalone
    {"framework": "nextjs-default", "language": "nextjs", "template_dir": "nextjs/default", "package_manager": "npm", "dev_command": "npm run dev"},
]

# Note: TypeScript frameworks share enum values with JS (express, nestjs).
# The registry key is Framework enum which doesn't distinguish TS vs JS.
# We handle this by using language-specific template_dir lookup at generation time.

# Build a mapping of (Language, Framework) -> FrameworkInfo for language-aware lookups
LANGUAGE_FRAMEWORK_MAP: dict[tuple[Language, Framework], FrameworkInfo] = {}

for _def in _FRAMEWORK_DEFINITIONS:
    _info = FrameworkInfo(
        framework=Framework(_def["framework"]),
        language=Language(_def["language"]),
        template_dir=_def["template_dir"],
        package_manager=_def["package_manager"],
        dev_command=_def["dev_command"],
    )
    LANGUAGE_FRAMEWORK_MAP[(Language(_def["language"]), Framework(_def["framework"]))] = _info
    # Also register in the class registry (last one wins for same framework)
    FrameworkInfo.register(_info)


def get_frameworks_for_language(language: Language) -> list[FrameworkInfo]:
    """Get all frameworks available for a specific language."""
    return [info for key, info in LANGUAGE_FRAMEWORK_MAP.items() if key[0] == language]


def get_framework_info(language: Language, framework: Framework) -> FrameworkInfo | None:
    """Get framework info for a specific language + framework combination."""
    return LANGUAGE_FRAMEWORK_MAP.get((language, framework))
