"""Unit tests for 12-factor load helpers."""

import pytest

from superconf.configuration import ConfigurationObj
from superconf.fields import FieldBool, FieldInt, FieldString
from superconf.twelve_factor import (
    TwelveFactorError,
    build_12factor_view,
    from_12factor,
    load_12factor,
)

pytestmark = pytest.mark.unit


class AppConfig(ConfigurationObj):
    """Minimal schema for twelve-factor tests."""

    name = FieldString(default="default_name")
    enabled = FieldBool(default=True)
    count = FieldInt(default=0)


class PrefixedAppConfig(ConfigurationObj):
    """Schema with Meta.env_prefix."""

    class Meta:
        """Class-level env mapping defaults."""

        env_prefix = "APP"

    name = FieldString(default="default_name")
    enabled = FieldBool(default=True)
    count = FieldInt(default=0)


def test_env_overrides_defaults_and_casts():
    """Env strings override defaults and cast on bind."""
    environ = {
        "APP__ENABLED": "false",
        "APP__COUNT": "42",
    }
    config = load_12factor(AppConfig, env_prefix="APP", environ=environ)
    assert config.name == "default_name"
    assert config.enabled is False
    assert config.count == 42


def test_cli_beats_env_beats_file_beats_defaults(tmp_path):
    """Full precedence: cli > env > file > defaults."""
    config_path = tmp_path / "config.yml"
    config_path.write_text(
        "name: from-file\nenabled: true\ncount: 10\n",
        encoding="utf-8",
    )
    environ = {
        "APP__NAME": "from-env",
        "APP__ENABLED": "false",
        "APP__COUNT": "20",
    }
    config = from_12factor(
        AppConfig,
        env_prefix="APP",
        file=config_path,
        cli={"count": 30},
        environ=environ,
    )
    assert config.name == "from-env"
    assert config.enabled is False
    assert config.count == 30


def test_meta_env_prefix_when_omitted():
    """Meta.env_prefix is used when env_prefix= is omitted."""
    environ = {"APP__COUNT": "7"}
    config = from_12factor(PrefixedAppConfig, environ=environ)
    assert config.count == 7


def test_file_only_overrides_defaults(tmp_path):
    """File layer beats schema defaults without env."""
    config_path = tmp_path / "app.json"
    config_path.write_text(
        '{"name": "json-app", "count": 3}',
        encoding="utf-8",
    )
    config = load_12factor(AppConfig, file=config_path)
    assert config.name == "json-app"
    assert config.count == 3
    assert config.enabled is True


def test_unknown_file_suffix_raises(tmp_path):
    """Unsupported file suffixes raise TwelveFactorError."""
    bad_path = tmp_path / "config.ini"
    bad_path.write_text("name=x\n", encoding="utf-8")
    with pytest.raises(TwelveFactorError, match="Unsupported config file suffix"):
        load_12factor(AppConfig, file=bad_path)


def test_build_12factor_view_explain():
    """build_12factor_view exposes layers for debugging."""
    environ = {"APP__NAME": "env-name"}
    view = build_12factor_view(
        PrefixedAppConfig,
        environ=environ,
        cli={"name": "cli-name"},
    )
    assert view.get("name") == "cli-name"
    merged = view.materialize()
    assert merged["name"] == "cli-name"
