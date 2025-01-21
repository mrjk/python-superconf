import os
import pytest
from pathlib import Path

from superconf.extra.xdg import XDGConfig, XDGException
from superconf.configuration import Configuration


@pytest.fixture
def mock_env(monkeypatch, tmp_path):
    """Mock environment with basic XDG variables."""
    home_dir = tmp_path / "home/testuser"
    etc_dir = tmp_path / "etc"
    usr_dir = tmp_path / "usr"
    run_dir = tmp_path / "run"

    test_env = {
        "HOME": str(home_dir),
        "USER": "testuser",
        "XDG_CONFIG_HOME": str(home_dir / ".config"),
        "XDG_DATA_HOME": str(home_dir / ".local/share"),
        "XDG_CACHE_HOME": str(home_dir / ".cache"),
        "XDG_STATE_HOME": str(home_dir / ".local/state"),
        "XDG_RUNTIME_DIR": str(run_dir / "user/1000"),
        "XDG_CONFIG_DIRS": f"{etc_dir / 'xdg'}:{usr_dir / 'local/etc/xdg'}",
        "XDG_DATA_DIRS": f"{usr_dir / 'local/share'}:{usr_dir / 'share'}",
    }

    # Create base directories
    (home_dir / ".config").mkdir(parents=True, exist_ok=True)
    (home_dir / ".local/share").mkdir(parents=True, exist_ok=True)
    (home_dir / ".cache").mkdir(parents=True, exist_ok=True)
    (home_dir / ".local/state").mkdir(parents=True, exist_ok=True)
    (run_dir / "user/1000").mkdir(parents=True, exist_ok=True)
    (etc_dir / "xdg").mkdir(parents=True, exist_ok=True)
    (usr_dir / "local/etc/xdg").mkdir(parents=True, exist_ok=True)
    (usr_dir / "local/share").mkdir(parents=True, exist_ok=True)
    (usr_dir / "share").mkdir(parents=True, exist_ok=True)

    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    return test_env


def test_xdg_config_basic_env(mock_env, tmp_path):
    """Test basic XDG environment variable expansion."""
    config = XDGConfig()
    home_dir = tmp_path / "home/testuser"
    etc_dir = tmp_path / "etc"
    usr_dir = tmp_path / "usr"
    run_dir = tmp_path / "run"

    assert config.XDG_CONFIG_HOME == str(home_dir / ".config")
    assert config.XDG_DATA_HOME == str(home_dir / ".local/share")
    assert config.XDG_CACHE_HOME == str(home_dir / ".cache")
    assert config.XDG_STATE_HOME == str(home_dir / ".local/state")
    assert config.XDG_RUNTIME_DIR == str(run_dir / "user/1000")
    assert config.XDG_CONFIG_DIRS == [
        str(etc_dir / "xdg"),
        str(usr_dir / "local/etc/xdg"),
    ]
    assert config.XDG_DATA_DIRS == [
        str(usr_dir / "local/share"),
        str(usr_dir / "share"),
    ]


from pprint import pprint


def test_xdg_config_get_config_file(mock_env, tmp_path):
    """Test get_config_file with various scenarios."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test app directory
    app_config_dir = home_dir / ".config/testapp"
    app_config_dir.mkdir(parents=True, exist_ok=True)

    # Test default config file (no name)
    expected = Path(str(app_config_dir) + ".yml")
    assert config.get_config_file() == expected

    # Test named config file
    expected = app_config_dir / "settings.yml"
    assert config.get_config_file("settings") == expected

    # Test full path with extension
    expected = app_config_dir / "config.yml"
    assert config.get_config_file("config.yml") == expected


def test_xdg_config_get_config_dir(mock_env, tmp_path):
    """Test get_config_dir with various scenarios."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test directories
    base_dir = home_dir / ".config/testapp"
    base_dir.mkdir(parents=True, exist_ok=True)
    (base_dir / "subconfig").mkdir(exist_ok=True)
    (base_dir / "subconfig/sub1").mkdir(parents=True, exist_ok=True)

    # Test default config directory (no name)
    expected = base_dir
    assert config.get_config_dir() == expected

    # Test named subdirectory
    expected = base_dir / "subconfig"
    assert config.get_config_dir("subconfig") == expected

    # Test nested subdirectory
    expected = base_dir / "subconfig/sub1"
    assert config.get_config_dir("subconfig/sub1") == expected


def test_xdg_config_invalid_item(mock_env):
    """Test handling of invalid XDG items."""
    config = XDGConfig()

    with pytest.raises(XDGException) as exc_info:
        config._get_file("INVALID_ITEM")
    assert "Unknown item" in str(exc_info.value)


def test_xdg_config_file_extensions(mock_env, tmp_path):
    """Test file extension handling in config file resolution."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test files
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    test_files = {
        "config.yml": "yml content",
        "config.yaml": "yaml content",
        "config.json": "json content",
    }

    for fname, content in test_files.items():
        (config_dir / fname).write_text(content)

    # Test that we get the first available extension
    result = config.get_config_file("config")
    assert result.suffix in [".yml", ".yaml", ".json"]


def test_xdg_config_read_file(mock_env, tmp_path):
    """Test reading configuration files with different formats."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test files
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Create YAML config
    yaml_content = """
    key1: value1
    key2: 
      nested: value2
    """
    (config_dir / "config.yml").write_text(yaml_content)

    # Create JSON config
    json_content = """
    {
        "key1": "value1",
        "key2": {
            "nested": "value2"
        }
    }
    """
    (config_dir / "config.json").write_text(json_content)

    # Test reading YAML
    result = config.read_file("XDG_CONFIG_HOME", "config")
    assert result["key1"] == "value1"
    assert result["key2"]["nested"] == "value2"


def test_xdg_config_in_app(mock_env, tmp_path):
    """Test XDG configuration as part of an application."""

    # TODO: This should work outside the class, before env in changed !
    class TestApp(Configuration):
        """Test application configuration."""

        class Meta:
            app_name = "testapp"
            env_prefix = "TEST_APP"

        runtime = XDGConfig()

    app = TestApp()
    home_dir = tmp_path / "home/testuser"

    # Create test config
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Verify runtime configuration
    assert isinstance(app.runtime, XDGConfig)
    assert app.runtime.get_config_dir() == home_dir / ".config"
