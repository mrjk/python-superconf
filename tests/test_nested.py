import pytest
from superconf.exceptions import UnknownSetting
from superconf.loaders import Dict

def test_nested_config_structure(nested_config):
    """Test the structure of nested configuration"""
    assert nested_config.name == "MyApp"
    assert nested_config.version == "1.0.0"
    assert hasattr(nested_config, "database")
    assert hasattr(nested_config, "features")

def test_nested_database_config(nested_config):
    """Test nested database configuration values"""
    db = nested_config.database
    assert db.host == "localhost"
    assert db.port == 5432
    
    # Test extra fields functionality
    with pytest.raises(AttributeError):
        assert db.credentials["username"] == "admin"
    with pytest.raises(AttributeError):
        assert db.credentials["password"] == "secret"

def test_nested_list_values(nested_config):
    """Test list values in nested configuration"""
    features = nested_config.features
    assert isinstance(features, list)
    assert len(features) == 3
    assert "auth" in features
    assert "api" in features
    assert "admin" in features

def test_nested_config_inheritance(nested_config_class):
    """Test configuration inheritance and overrides"""
    # Create config with overridden values
    override_data = {
        "database": {
            "host": "db.example.com",
            "port": 3306,
            "credentials": {
                "username": "user",
                "password": "pass"
            }
        }
    }
    config = nested_config_class(loaders=[Dict(override_data)])
    
    assert config.database.host == "db.example.com"
    assert config.database.port == 3306
    assert config.database["credentials"]["username"] == "user"

    # Test that accessing undefined fields raises an exception
    with pytest.raises(AttributeError):
        _ = config.database.credentials

def test_nested_config_validation(nested_config):
    """Test validation in nested configurations"""
    db = nested_config.database
    
    # Test accessing non-existent field
    with pytest.raises(AttributeError):
        _ = db.nonexistent
    
    # Test accessing non-existent nested field
    with pytest.raises(AttributeError):
        _ = db.credentials["nonexistent"]

@pytest.mark.parametrize("path,expected", [
    (["name"], "MyApp"),
    (["database", "host"], "localhost"),
    # (["database", "credentials", "username"], "admin"),
    (["features", 0], "auth"),
])
def test_nested_path_access(nested_config, path, expected):
    """Test accessing nested values through paths"""
    value = nested_config
    for key in path:
        if isinstance(key, int):
            value = value[key]
        else:
            value = getattr(value, key)
    assert value == expected 