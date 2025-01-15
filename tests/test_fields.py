import pytest
from superconf.exceptions import InvalidCastConfiguration
from superconf.loaders import Dict


def test_field_types(typed_config):
    """Test different field types and their default values"""
    assert isinstance(typed_config.debug, bool)
    assert isinstance(typed_config.port, int)
    assert isinstance(typed_config.name, str)
    assert isinstance(typed_config.settings, dict)
    assert isinstance(typed_config.plugins, list)

def test_field_defaults(typed_config):
    """Test default values for different field types"""
    assert typed_config.debug is False
    assert typed_config.port == 8080
    assert typed_config.name == "app"
    assert typed_config.settings == {}
    assert typed_config.plugins == []

@pytest.mark.parametrize("field,value,expected", [
    ("debug", "true", True),
    ("debug", "1", True),
    ("debug", "yes", True),
    ("debug", "false", False),
    ("debug", "0", False),
    ("debug", "no", False),
    ("port", "8000", 8000),
    ("name", "test-app", "test-app"),
    ("plugins", ["one", "two"], ["one", "two"]),
])
def test_field_value_casting(typed_config_class, field, value, expected):
    """Test field type casting with various input values"""
    config = typed_config_class(loaders=[Dict({field: value})])
    assert getattr(config, field) == expected

def test_field_validation_errors(typed_config_class):
    """Test field validation and error handling"""
    # Test invalid port number - config creation should succeed but value access should fail
    config = typed_config_class(loaders=[Dict({"port": "invalid"})])
    with pytest.raises(InvalidCastConfiguration):
        _ = config.port
    
    # Test invalid boolean
    config = typed_config_class(loaders=[Dict({"debug": "invalid"})])
    with pytest.raises(InvalidCastConfiguration):
        _ = config.debug


def test_field_dict_operations(typed_config_class):
    """Test dictionary field operations"""
    # Test setting dictionary values
    test_settings = {"key1": "value1", "key2": "value2"}
    config = typed_config_class(loaders=[Dict({"settings": test_settings})])
    assert config.settings == test_settings
    
    # Test nested dictionary values
    nested_settings = {"level1": {"level2": "value"}}
    config = typed_config_class(loaders=[Dict({"settings": nested_settings})])
    assert config.settings["level1"]["level2"] == "value"

def test_field_list_operations(typed_config_class):
    """Test list field operations"""
    # Test list with simple values
    config = typed_config_class(loaders=[Dict({"plugins": ["plugin1", "plugin2"]})])
    assert len(config.plugins) == 2
    assert "plugin1" in config.plugins
    
    # Test list with mixed types
    mixed_list = ["string", 123, True]
    config = typed_config_class(loaders=[Dict({"plugins": mixed_list})])
    assert config.plugins == mixed_list 