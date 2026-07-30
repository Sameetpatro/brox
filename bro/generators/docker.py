"""Docker generator — Dockerfile and docker-compose.yml."""

from __future__ import annotations

from pathlib import Path

from bro.generators.base import BaseGenerator
from bro.models.feature import Feature
from bro.models.project import ProjectConfig
from bro.utils.fs import safe_write
from bro.utils.logger import get_logger

logger = get_logger(__name__)

DOCKERFILES: dict[str, str] = {
    "python": """FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "go": """FROM golang:1.22-alpine AS builder

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -o server .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/server .

EXPOSE 8080

CMD ["./server"]
""",
    "javascript": """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "src/index.js"]
""",
    "typescript": """FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY package*.json ./

EXPOSE 3000

CMD ["node", "dist/index.js"]
""",
    "rust": """FROM rust:1.76-slim AS builder

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo "fn main(){}" > src/main.rs && cargo build --release && rm -rf src

COPY . .
RUN cargo build --release

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/app /usr/local/bin/app

EXPOSE 8080

CMD ["app"]
""",
    "java": """FROM maven:3.9-eclipse-temurin-21 AS builder

WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline

COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:21-jre-alpine
COPY --from=builder /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
""",
    "kotlin": """FROM gradle:8-jdk21 AS builder

WORKDIR /app
COPY build.gradle.kts settings.gradle.kts ./
COPY gradle ./gradle
RUN gradle dependencies --no-daemon

COPY . .
RUN gradle shadowJar --no-daemon

FROM eclipse-temurin:21-jre-alpine
COPY --from=builder /app/build/libs/*-all.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
""",
}


def _compose_template(config: ProjectConfig) -> str:
    """Generate docker-compose.yml content."""
    services = f"""  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/{config.safe_name}
      - REDIS_URL=redis://redis:6379/0
    depends_on:"""

    deps = []
    if config.has_feature(Feature.POSTGRESQL):
        deps.append("db")
    if config.has_feature(Feature.REDIS):
        deps.append("redis")

    if deps:
        services += "\n" + "\n".join(f"      - {d}" for d in deps)
    services += "\n    restart: unless-stopped\n"

    extra_services = ""
    volumes = ""

    if config.has_feature(Feature.POSTGRESQL):
        extra_services += f"""
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: {config.safe_name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
"""
        volumes += "  postgres_data:\n"

    if config.has_feature(Feature.REDIS):
        extra_services += """
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
"""
        volumes += "  redis_data:\n"

    compose = f"""services:
{services}{extra_services}"""

    if volumes:
        compose += f"\nvolumes:\n{volumes}"

    return compose


class DockerGenerator(BaseGenerator):
    """Generates Dockerfile."""

    @property
    def name(self) -> str:
        return "Docker"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.DOCKER)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        created: list[Path] = []

        lang = config.language.value
        if lang in ("react", "nextjs"):
            lang = "javascript"

        dockerfile = DOCKERFILES.get(lang, DOCKERFILES["python"])
        path = project_dir / "Dockerfile"
        if safe_write(path, dockerfile):
            created.append(path)

        # .dockerignore
        dockerignore = ".git\nnode_modules\nvenv\n.venv\n__pycache__\n.env\ndist\nbuild\ntarget\n"
        ignore_path = project_dir / ".dockerignore"
        if safe_write(ignore_path, dockerignore):
            created.append(ignore_path)

        return created


class DockerComposeGenerator(BaseGenerator):
    """Generates docker-compose.yml."""

    @property
    def name(self) -> str:
        return "Docker Compose"

    def should_run(self, config: ProjectConfig) -> bool:
        return config.has_feature(Feature.DOCKER_COMPOSE)

    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        created: list[Path] = []
        content = _compose_template(config)
        path = project_dir / "docker-compose.yml"
        if safe_write(path, content):
            created.append(path)
        return created
