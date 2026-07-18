"""Unit tests for the standalone environment codec in lib.codec_env."""

import pytest

from superconf.lib.codec_env import (
    CodecEnvConflictError,
    CodecEnvPrefixError,
    expand_env,
    flatten_env,
    to_dotenv,
)

pytestmark = pytest.mark.unit


def test_expand_nested_dict_and_list():
    """Expand prefix paths into nested dicts and lists."""
    environ = {
        "APP__DATABASE__HOST": "db.internal",
        "APP__DATABASE__PORT": "5432",
        "APP__TAGS__0": "api",
        "APP__TAGS__1": "prod",
        "APP__BACKENDS__0__PORT": "8080",
        "APP__BACKENDS__1__ENABLED": "true",
        "OTHER__IGNORED": "nope",
    }
    result = expand_env(environ, prefix="APP")
    assert result == {
        "database": {"host": "db.internal", "port": "5432"},
        "tags": ["api", "prod"],
        "backends": [
            {"port": "8080"},
            {"enabled": "true"},
        ],
    }


def test_expand_compacts_list_holes_silently():
    """Missing list indexes are dropped without warning."""
    environ = {
        "APP__TAGS__0": "a",
        "APP__TAGS__2": "c",
    }
    result = expand_env(environ, prefix="app")
    assert result == {"tags": ["a", "c"]}


def test_expand_accepts_trailing_separator_on_prefix():
    """Prefix may be passed with a trailing separator."""
    result = expand_env({"APP__NAME": "x"}, prefix="APP__")
    assert result == {"name": "x"}


def test_expand_prefix_is_case_insensitive():
    """Prefix matching ignores case on env keys."""
    result = expand_env({"app__Name": "x"}, prefix="App")
    assert result == {"name": "x"}


def test_expand_empty_prefix_raises():
    """Empty prefix is rejected."""
    with pytest.raises(CodecEnvPrefixError):
        expand_env({"APP__NAME": "x"}, prefix="")


def test_expand_leaf_container_conflict_raises():
    """A leaf and a nested path at the same key conflict."""
    environ = {
        "APP__DB": "hello",
        "APP__DB__HOST": "x",
    }
    with pytest.raises(CodecEnvConflictError):
        expand_env(environ, prefix="APP")


def test_expand_container_then_leaf_conflict_raises():
    """Setting a leaf over an existing container conflicts."""
    environ = {
        "APP__DB__HOST": "x",
        "APP__DB": "hello",
    }
    with pytest.raises(CodecEnvConflictError):
        expand_env(environ, prefix="APP")


def test_flatten_nested_structure():
    """Flatten nested dict/list structures to PREFIX__PATH keys."""
    data = {
        "database": {"host": "db.internal", "port": 5432},
        "tags": ["api", "prod"],
        "enabled": True,
        "debug": False,
    }
    result = flatten_env(data, prefix="APP")
    assert result == {
        "APP__DATABASE__HOST": "db.internal",
        "APP__DATABASE__PORT": "5432",
        "APP__DEBUG": "false",
        "APP__ENABLED": "true",
        "APP__TAGS__0": "api",
        "APP__TAGS__1": "prod",
    }


def test_flatten_skips_none_by_default():
    """None values are omitted when skip_none is True."""
    data = {"name": "app", "hint": None}
    result = flatten_env(data, prefix="APP")
    assert result == {"APP__NAME": "app"}


def test_flatten_emits_empty_string_when_skip_none_false():
    """None becomes an empty string when skip_none is False."""
    data = {"name": "app", "hint": None}
    result = flatten_env(data, prefix="APP", skip_none=False)
    assert result == {"APP__HINT": "", "APP__NAME": "app"}


def test_roundtrip_expand_flatten_strings():
    """expand(flatten(...)) preserves string-only nested data."""
    original = {
        "database": {"host": "db.internal", "port": "5432"},
        "tags": ["api", "prod"],
        "backends": [{"port": "8080"}, {"enabled": "true"}],
    }
    flat = flatten_env(original, prefix="APP")
    restored = expand_env(flat, prefix="APP")
    assert restored == original


def test_to_dotenv_and_export():
    """Render flat maps as dotenv and export lines."""
    env_map = {"APP__NAME": "my app", "APP__OK": "1"}
    dotenv_text = to_dotenv(env_map)
    assert 'APP__NAME="my app"' in dotenv_text
    assert "APP__OK=1" in dotenv_text

    export_text = to_dotenv(env_map, export=True)
    assert export_text.startswith("export ")
    assert "export APP__OK=1" in export_text
