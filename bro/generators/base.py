"""Base generator — Abstract base class for all generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from bro.models.project import ProjectConfig
from bro.utils.logger import get_logger

logger = get_logger(__name__)


class BaseGenerator(ABC):
    """Abstract base class for project component generators."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Generator name for display and logging."""
        ...

    @abstractmethod
    def generate(self, config: ProjectConfig, project_dir: Path) -> list[Path]:
        """Generate files/configs for this component.

        Returns list of created file paths.
        """
        ...

    def should_run(self, config: ProjectConfig) -> bool:
        """Whether this generator should run for the given config."""
        return True
