"""Tests for config module."""

from pathlib import Path
import tempfile

from bro.config.schema import BroConfig
from bro.config.manager import ConfigManager
from bro.models.feature import Feature
from bro.models.language import Language, Framework


def test_default_config() -> None:
    """Test default config values."""
    config = BroConfig()
    assert config.default_language == Language.PYTHON
    assert config.default_framework == Framework.FASTAPI
    assert config.always_git is True
    assert config.always_docker is False


def test_quick_features() -> None:
    """Test quick features generation from config."""
    config = BroConfig(always_git=True, always_docker=True, always_redis=False)
    features = config.get_quick_features()
    assert Feature.GIT in features
    assert Feature.DOCKER in features
    assert Feature.REDIS not in features


def test_config_save_load() -> None:
    """Test config save and load round-trip."""
    with tempfile.TemporaryDirectory() as tmpdir:
        config_path = Path(tmpdir) / "config.yaml"
        manager = ConfigManager(config_path=config_path)

        # Save custom config
        config = BroConfig(default_language=Language.GO, always_docker=True)
        manager.save(config)

        # Reload
        manager._config = None  # Clear cache
        loaded = manager.load()
        assert loaded.default_language == Language.GO
        assert loaded.always_docker is True
