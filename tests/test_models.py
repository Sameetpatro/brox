"""Tests for models."""

from bro.models.language import Language, Framework, get_frameworks_for_language
from bro.models.feature import Feature, get_default_features
from bro.models.project import ProjectConfig


def test_languages_have_display_names() -> None:
    """Test all languages have display names."""
    for lang in Language:
        assert lang.display_name
        assert lang.icon
        assert lang.color


def test_frameworks_have_display_names() -> None:
    """Test all frameworks have display names."""
    for fw in Framework:
        assert fw.display_name
        assert fw.description


def test_get_frameworks_for_language() -> None:
    """Test that we can get frameworks for each language."""
    python_frameworks = get_frameworks_for_language(Language.PYTHON)
    assert len(python_frameworks) == 3  # FastAPI, Django, Flask

    go_frameworks = get_frameworks_for_language(Language.GO)
    assert len(go_frameworks) == 3  # Gin, Fiber, Echo


def test_features_have_metadata() -> None:
    """Test all features have display names and descriptions."""
    for feature in Feature:
        assert feature.display_name
        assert feature.description
        assert feature.icon


def test_default_features() -> None:
    """Test default features list."""
    defaults = get_default_features()
    assert Feature.GIT in defaults
    assert Feature.README in defaults
    assert Feature.DOCKER not in defaults


def test_project_config() -> None:
    """Test ProjectConfig model."""
    config = ProjectConfig(
        name="test-project",
        language=Language.PYTHON,
        framework=Framework.FASTAPI,
        features=[Feature.GIT, Feature.DOCKER],
    )
    assert config.safe_name == "test_project"
    assert config.has_feature(Feature.GIT)
    assert config.has_feature(Feature.DOCKER)
    assert not config.has_feature(Feature.REDIS)
