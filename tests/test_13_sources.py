"""Unit tests for configuration data sources."""

import pytest

from superconf.configuration import ConfigurationObj
from superconf.fields import FieldBool, FieldInt, FieldString
from superconf.sources import (
    ConfigSource,
    DictSource,
    EnvSource,
    JsonSource,
    SourceLoadError,
    TomlSource,
    YamlSource,
)

pytestmark = pytest.mark.unit


def test_dict_source_load_and_dump():
    """DictSource round-trips an in-memory mapping."""
    source = DictSource("cli", {"name": "app", "workers": 2})
    assert source.load() == {"name": "app", "workers": 2}
    assert source.dump({"x": 1}) == {"x": 1}


def test_dict_source_factory():
    """DictSource accepts a zero-arg factory."""
    source = DictSource("cli", lambda: {"ok": True})
    assert source.load() == {"ok": True}


def test_env_source_load_and_dump(tmp_path):
    """EnvSource expands and flattens PREFIX__PATH keys."""
    environ = {
        "APP__DB__HOST": "localhost",
        "APP__TAGS__0": "a",
        "APP__TAGS__2": "c",
    }
    source = EnvSource("env", prefix="APP", environ=environ)
    assert source.load() == {"db": {"host": "localhost"}, "tags": ["a", "c"]}

    flat = source.dump({"enabled": True, "hint": None}, fmt="dict")
    assert flat == {"APP__ENABLED": "true"}

    dotenv_text = source.dump({"name": "x"}, fmt="dotenv")
    assert "APP__NAME=x" in dotenv_text


def test_json_source_string_and_file(tmp_path):
    """JsonSource loads from string and path."""
    source = JsonSource("file", data='{"name": "from-string"}')
    assert source.load() == {"name": "from-string"}
    assert '"name"' in source.dump({"name": "out"})

    path = tmp_path / "cfg.json"
    path.write_text('{"port": 9}', encoding="utf-8")
    file_source = JsonSource("file", path=path)
    assert file_source.load() == {"port": 9}


def test_yaml_source_string_and_file(tmp_path):
    """YamlSource loads from string and path."""
    source = YamlSource("file", data="name: from-yaml\n")
    assert source.load() == {"name": "from-yaml"}

    path = tmp_path / "cfg.yml"
    path.write_text("workers: 3\n", encoding="utf-8")
    assert YamlSource("file", path=path).load() == {"workers": 3}


def test_toml_source_load():
    """TomlSource loads TOML tables when a backend is available."""
    try:
        source = TomlSource("file", data='name = "toml-app"\nworkers = 4\n')
        result = source.load()
    except SourceLoadError:
        pytest.skip("tomllib/tomli not available")
    assert result["name"] == "toml-app"
    assert result["workers"] == 4


def test_config_source_strips_unset():
    """ConfigSource loads set values and strips NOT_SET."""

    class AppConfig(ConfigurationObj):
        name = FieldString(default="default-name")
        port = FieldInt(default=80)
        enabled = FieldBool(default=True)

    app = AppConfig(value={"name": "custom"})
    source = ConfigSource("defaults", app, nodefaults=True)
    loaded = source.load()
    assert loaded["name"] == "custom"
    assert "port" not in loaded
    assert "enabled" not in loaded

    with_defaults = ConfigSource("defaults", app, nodefaults=False).load()
    assert with_defaults["port"] == 80
    assert with_defaults["enabled"] is True


def test_json_source_requires_object_root():
    """JSON arrays are rejected as roots."""
    source = JsonSource("file", data="[1, 2]")
    with pytest.raises(SourceLoadError):
        source.load()
