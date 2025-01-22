# pylint: skip-file


import os
from pathlib import Path
from pprint import pprint

import pytest

from superconf.configuration import Configuration
from superconf.extra.xdg import XDGConfig, XDGException
from superconf.fields import FieldConf


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

        runtime = FieldConf(children_class=XDGConfig)

    app = TestApp()
    home_dir = tmp_path / "home/testuser"

    # Create test config
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Verify runtime configuration
    assert isinstance(app.runtime, XDGConfig)
    assert app.runtime.get_config_dir() == home_dir / ".config" / "testapp"


def test_xdg_config_default(mock_env, tmp_path):
    """Test XDG configuration as part of an application."""

    # TODO: This should work outside the class, before env in changed !
    class TestApp(Configuration):
        """Test application configuration."""

        runtime = FieldConf(children_class=XDGConfig)

    app = TestApp()
    home_dir = tmp_path / "home/testuser"

    # Create test config
    config_dir = home_dir / ".config/TestApp"
    config_dir.mkdir(parents=True)

    # Verify runtime configuration
    assert isinstance(app.runtime, XDGConfig)
    print(home_dir / ".config" / "TestApp")
    print(app.runtime.get_config_dir())
    assert app.runtime.get_config_dir() == home_dir / ".config" / "TestApp"


def test_xdg_config_custom_dirs(mock_env, monkeypatch):
    """Test XDG configuration with custom XDG_CONFIG_DIRS."""
    custom_dirs = "$HOME/dir1:dir2:dir3"
    monkeypatch.setenv("XDG_CONFIG_DIRS", custom_dirs)

    class App(Configuration):
        runtime = FieldConf(children_class=XDGConfig)

    app = App()
    # pprint(app.__dict__)
    # pprint(app.get_values())
    assert isinstance(app.runtime, XDGConfig)
    # Verify the custom dirs are properly expanded
    home = os.environ.get("HOME")
    expected_dirs = [os.path.expandvars(f"{home}/dir1"), "dir2", "dir3"]
    pprint(expected_dirs)
    pprint(app.runtime.XDG_CONFIG_DIRS)
    assert app.runtime.XDG_CONFIG_DIRS == expected_dirs


def test_xdg_config_check_stacks(mock_env, tmp_path):
    """Test check_stacks functionality."""

    class App(Configuration):
        # meta__app_name = "MySUPERAPP"

        class Meta:
            cache = True
            app_name = "MySUPERAPP"
            env_prefix = "MY_APPLICATION"

        runtime = FieldConf(children_class=XDGConfig)

        def check_stacks(self):
            return self.runtime._get_file("XDG_CONFIG_HOME")

        def check_stacks2(self):
            return self.runtime._get_file("XDG_CONFIG_HOME", "TUTU")

    app = App()
    # pprint(app.query_cfg("app_name", report=True), width=200)
    # pprint(app.runtime.query_cfg("app_name", report=True), width=200)

    result = app.check_stacks()
    # Should return a Path object pointing to the app's config directory
    assert isinstance(result, Path)
    print(result)
    assert str(result).endswith("MySUPERAPP.yml")


def test_xdg_read_file_locations(mock_env, tmp_path):
    """Test reading files from different XDG locations."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test files in different XDG locations
    config_home = home_dir / ".config/testapp"
    config_home.mkdir(parents=True)

    test_configs = {"config.yml": "key: value1", "config.user.yml": "key: value2"}

    for fname, content in test_configs.items():
        (config_home / fname).write_text(content)

    # Test reading from XDG_CONFIG_HOME
    result1 = config.read_file("XDG_CONFIG_HOME", "config")
    assert result1["key"] == "value1"

    # Test reading user config
    result2 = config.read_file("XDG_CONFIG_HOME", "config.user")
    assert result2["key"] == "value2"

    # Test reading non-existent file
    result3 = config.read_file("XDG_CONFIG_HOME", "nonexistent")
    assert result3 is None


def test_xdg_config_field_integration(mock_env):
    """Test XDGConfig integration with FieldConf."""

    class App(Configuration):
        class Meta:
            app_name = "testapp"
            env_prefix = "TEST_APP"

        runtime = FieldConf(children_class=XDGConfig)

    app = App()
    assert isinstance(app.runtime, XDGConfig)
    assert App.Meta.app_name == "testapp"
    assert app.runtime.query_cfg("app_name") == "testapp"
    assert app.runtime.query_cfg("env_prefix") == "TEST_APP"


def test_xdg_config_create_and_load(mock_env, tmp_path):
    """Test creating and loading config files in XDG paths."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory and files
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Create different config files with test data
    configs = {
        "settings.yml": """
            database:
                host: localhost
                port: 5432
                name: testdb
            logging:
                level: INFO
                file: /var/log/app.log
            """,
        "auth.json": """
            {
                "secret_key": "test123",
                "allowed_hosts": ["localhost", "127.0.0.1"],
                "timeout": 3600
            }
            """,
    }

    for fname, content in configs.items():
        (config_dir / fname).write_text(content)

    # Test loading YAML config
    yaml_result = config.read_file("XDG_CONFIG_HOME", "settings")
    assert yaml_result["database"]["host"] == "localhost"
    assert yaml_result["database"]["port"] == 5432
    assert yaml_result["logging"]["level"] == "INFO"

    # Test loading JSON config
    json_result = config.read_file("XDG_CONFIG_HOME", "auth")
    assert json_result["secret_key"] == "test123"
    assert "localhost" in json_result["allowed_hosts"]
    assert json_result["timeout"] == 3600

    # Test loading with full path including extension
    yaml_result_full = config.read_file("XDG_CONFIG_HOME", "settings.yml")
    assert yaml_result_full == yaml_result


def test_xdg_config_load_from_multiple_locations(mock_env, tmp_path):
    """Test loading configs from different XDG locations with precedence."""
    config = XDGConfig()
    config.meta__app_name = "testapp"

    # Setup directories
    home_dir = tmp_path / "home/testuser"
    etc_dir = tmp_path / "etc/xdg/testapp"
    usr_dir = tmp_path / "usr/local/etc/xdg/testapp"

    # Create config directories
    config_home = home_dir / ".config/testapp"
    config_home.mkdir(parents=True)
    etc_dir.mkdir(parents=True)
    usr_dir.mkdir(parents=True)

    # Create config files with different values
    configs = {
        str(
            config_home / "config.yml"
        ): """
            setting: home_value
            common: home_common
            """,
        str(
            etc_dir / "config.yml"
        ): """
            setting: etc_value
            common: etc_common
            etc_only: etc_specific
            """,
        str(
            usr_dir / "config.yml"
        ): """
            setting: usr_value
            common: usr_common
            usr_only: usr_specific
            """,
    }

    for fpath, content in configs.items():
        Path(fpath).write_text(content)

    # Test loading - should get home value due to precedence
    result = config.read_file("XDG_CONFIG_HOME", "config")
    assert result["setting"] == "home_value"
    assert result["common"] == "home_common"


def test_xdg_config_write_file_basic(mock_env, tmp_path):
    """Test basic write_file functionality with dictionary data."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Test data
    test_data = {
        "database": {"host": "localhost", "port": 5432, "name": "testdb"},
        "settings": {"debug": True, "timeout": 30},
    }

    # Write data to config file
    config.write_file("XDG_CONFIG_HOME", test_data, "config")

    # Read back and verify
    result = config.read_file("XDG_CONFIG_HOME", "config")
    assert result == test_data
    assert result["database"]["port"] == 5432
    assert result["settings"]["debug"] is True


def test_xdg_config_write_file_list(mock_env, tmp_path):
    """Test write_file functionality with list data."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Test data
    test_data = [
        {"name": "item1", "value": 1},
        {"name": "item2", "value": 2},
        {"name": "item3", "value": 3},
    ]

    # Write data to config file
    config.write_file("XDG_CONFIG_HOME", test_data, "config.list")

    # Read back and verify
    result = config.read_file("XDG_CONFIG_HOME", "config.list")
    assert result == test_data
    assert len(result) == 3
    assert result[1]["name"] == "item2"


def test_xdg_config_write_file_overwrite(mock_env, tmp_path):
    """Test write_file overwrite behavior."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Initial data
    initial_data = {"key": "initial_value"}
    config.write_file("XDG_CONFIG_HOME", initial_data, "config")

    # New data
    new_data = {"key": "new_value"}
    config.write_file("XDG_CONFIG_HOME", new_data, "config")

    # Read back and verify
    result = config.read_file("XDG_CONFIG_HOME", "config")
    assert result == new_data
    assert result["key"] == "new_value"


def test_xdg_config_write_file_multiple_locations(mock_env, tmp_path):
    """Test writing files to different XDG locations."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Test data for different locations
    user_data = {"location": "user_config"}
    system_data = {"location": "system_config"}

    # Write to different locations
    config.write_file("XDG_CONFIG_HOME", user_data, "settings")

    # Read back and verify
    user_result = config.read_file("XDG_CONFIG_HOME", "settings")
    assert user_result == user_data
    assert user_result["location"] == "user_config"


def test_xdg_config_write_file_complex_data(mock_env, tmp_path):
    """Test write_file with complex nested data structures."""
    config = XDGConfig()
    config.meta__app_name = "testapp"
    home_dir = tmp_path / "home/testuser"

    # Create test config directory
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)

    # Complex test data
    test_data = {
        "server": {
            "hosts": ["host1", "host2", "host3"],
            "ports": [8080, 8081, 8082],
            "settings": {
                "timeout": 30,
                "retries": 3,
                "flags": {"debug": True, "verbose": False},
            },
        },
        "users": [
            {"name": "user1", "roles": ["admin", "user"]},
            {"name": "user2", "roles": ["user"]},
        ],
    }

    # Write data
    config.write_file("XDG_CONFIG_HOME", test_data, "complex_config")

    # Read back and verify
    result = config.read_file("XDG_CONFIG_HOME", "complex_config")
    assert result == test_data
    assert result["server"]["hosts"] == ["host1", "host2", "host3"]
    assert result["server"]["settings"]["flags"]["debug"] is True
    assert len(result["users"]) == 2
    assert "admin" in result["users"][0]["roles"]


def test_xdg_config_write_file_errors(mock_env, tmp_path):
    """Test write_file error handling."""
    config = XDGConfig()
    config.meta__app_name = "testapp"

    # Test invalid item
    with pytest.raises(XDGException, match="Unknown item"):
        config.write_file("INVALID_ITEM", {}, "config")

    # Test unsupported format
    # with pytest.raises(XDGException, match="Unsupported file type: txt"):
    config.write_file("XDG_CONFIG_HOME", {}, "config.txt")

    # Test toml format (not implemented)
    with pytest.raises(NotImplementedError, match="Toml support not implemented"):
        config.write_file("XDG_CONFIG_HOME", {}, "config.toml")

    # Test ini format (not implemented)
    # with pytest.raises(XDGException, match="Unsupported file type: ini"):
    config.write_file("XDG_CONFIG_HOME", {}, "config.ini")


def test_xdg_config_read_file_errors(mock_env, tmp_path):
    """Test read_file error handling."""
    config = XDGConfig()
    config.meta__app_name = "testapp"

    # Test invalid item
    with pytest.raises(XDGException, match="Unknown item"):
        config.read_file("INVALID_ITEM", "config")

    # Test file not found
    # out = config.read_file("XDG_CONFIG_HOME", "nonexistent")
    # print ("YOOO")
    # pprint(out)
    # with pytest.raises(XDGException, match="Could not find any file"):
    config.read_file("XDG_CONFIG_HOME", "nonexistent")

    # Test unsupported format
    home_dir = tmp_path / "home/testuser"
    config_dir = home_dir / ".config/testapp"
    config_dir.mkdir(parents=True)
    (config_dir / "config.txt").write_text("invalid format")

    print("OUTPUT", (config_dir / "config.txt"))

    # with pytest.raises(NotImplementedError, match="Format not supported"):
    config.read_file("XDG_CONFIG_HOME", "config.txt")

    # Test toml format (not implemented)
    (config_dir / "config.toml").write_text("[section]\nkey = 'value'")
    with pytest.raises(NotImplementedError, match="Toml support not implemented"):
        config.read_file("XDG_CONFIG_HOME", "config.toml")

    # Test ini format (not implemented)
    # (config_dir / "config.ini").write_text("[section]\nkey = value")
    # with pytest.raises(NotImplementedError, match="Ini support is not implemented"):
    #     config.read_file("XDG_CONFIG_HOME", "config.ini")


def test_xdg_config_default_app_name(mock_env, tmp_path):
    """Test default app name handling when not explicitly set."""

    class CustomApp(Configuration):
        runtime = FieldConf(children_class=XDGConfig)

    app = CustomApp()

    # Test _get_file with default app name
    config_file = app.runtime._get_file("XDG_CONFIG_HOME")
    assert "CustomApp" in str(config_file)

    # Test _get_dir with default app name
    config_dir = app.runtime._get_dir("XDG_CONFIG_HOME")
    assert "CustomApp" in str(config_dir)


def test_xdg_config_return_handling(mock_env, tmp_path):
    """Test return value handling in various methods."""
    config = XDGConfig()
    config.meta__app_name = "testapp"

    # Test _get_file with empty result
    result = config._get_file("XDG_CONFIG_HOME", "nonexistent")
    assert result is not None  # Should return a Path object even if file doesn't exist

    # Test _get_dir with empty result
    result = config._get_dir("XDG_CONFIG_HOME", "nonexistent")
    assert (
        result is not None
    )  # Should return a Path object even if directory doesn't exist

    # Test _get_file with list return
    config.set_values({"XDG_CONFIG_DIRS": ["/path1", "/path2"]})
    result = config._get_file("XDG_CONFIG_DIRS")
    assert isinstance(result, list)
    assert len(result) == 2

    # Test _get_dir with list return
    result = config._get_dir("XDG_CONFIG_DIRS")
    assert isinstance(result, list)
    assert len(result) == 2


def test_xdg_config_get_dir_errors(mock_env, tmp_path):
    """Test error handling in _get_dir method."""
    config = XDGConfig()
    config.meta__app_name = "testapp"

    # Test invalid item
    with pytest.raises(XDGException, match="Unknown item"):
        config._get_dir("INVALID_ITEM")

    # Test with non-string app_name
    config.meta__app_name = 123  # Invalid app name type
    result = config._get_dir("XDG_CONFIG_HOME")
    assert "XDGConfig" in str(result)  # Should fall back to class name
