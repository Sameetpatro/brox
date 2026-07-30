"""Config manager — loads and saves ~/.bro/config.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from bro.config.defaults import BRO_HOME, CONFIG_FILE, TEMPLATES_DIR
from bro.config.schema import BroConfig
from bro.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages the global Bro configuration file."""

    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or CONFIG_FILE
        self._config: BroConfig | None = None

    def ensure_dirs(self) -> None:
        """Ensure ~/.bro/ and ~/.bro/templates/ exist."""
        BRO_HOME.mkdir(parents=True, exist_ok=True)
        TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

    def load(self) -> BroConfig:
        """Load config from disk, or return defaults if file doesn't exist."""
        if self._config is not None:
            return self._config

        self.ensure_dirs()

        if self.config_path.exists():
            try:
                raw = yaml.safe_load(self.config_path.read_text(encoding="utf-8"))
                if raw and isinstance(raw, dict):
                    self._config = BroConfig(**raw)
                    logger.debug("Config loaded from %s", self.config_path)
                    return self._config
            except Exception as e:
                logger.warning("Failed to load config: %s. Using defaults.", e)

        self._config = BroConfig()
        return self._config

    def save(self, config: BroConfig | None = None) -> None:
        """Save config to disk."""
        self.ensure_dirs()

        if config is not None:
            self._config = config

        if self._config is None:
            self._config = BroConfig()

        data = self._config.model_dump(mode="json")
        self.config_path.write_text(
            yaml.dump(data, default_flow_style=False, sort_keys=False),
            encoding="utf-8",
        )
        logger.debug("Config saved to %s", self.config_path)

    def update(self, **kwargs: object) -> BroConfig:
        """Update specific config fields and save."""
        config = self.load()
        updated = config.model_copy(update=kwargs)
        self.save(updated)
        return updated

    def reset(self) -> BroConfig:
        """Reset config to defaults."""
        self._config = BroConfig()
        self.save()
        return self._config


# ─── Singleton ────────────────────────────────────────────────────────────────

_manager: ConfigManager | None = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager singleton."""
    global _manager
    if _manager is None:
        _manager = ConfigManager()
    return _manager


def get_config() -> BroConfig:
    """Shortcut to get the current config."""
    return get_config_manager().load()
