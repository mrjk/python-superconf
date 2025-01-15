import pytest
from superconf.configuration import Configuration, Field
from superconf.exceptions import UnknownSetting
from superconf.common import NOT_SET


def test_basic_config_creation(basic_config_class):
    """Test basic configuration class creation"""
    config = basic_config_class()
    assert isinstance(config, Configuration)
    assert config.field1 is False
    assert config.field2 == "Default value"
    assert config.field3 == 42
    assert isinstance(config.field4, dict)


def test_config_with_data(config_with_dict_loader):
    """Test configuration with data from Dict loader"""
    config = config_with_dict_loader
    assert config.field1 is False
    assert config.field2 == "Default value"
    assert config.field3 == 42
    assert config.field4["item1"] is True
    assert config.field4["item2"] == 4333


def test_config_attribute_access(config_with_dict_loader):
    """Test different ways to access configuration values"""
    config = config_with_dict_loader
    # Test attribute access
    assert config.field1 is False
    # Test dictionary-style access
    assert config["field1"] is False
    # Test get_value method
    assert config.get_value("field1") is False


def test_unknown_field_access(empty_config):
    """Test accessing non-existent fields raises appropriate exceptions"""
    config = empty_config
    with pytest.raises(AttributeError):
        _ = config.nonexistent_field

    with pytest.raises(KeyError):
        _ = config["nonexistent_field"]


def test_meta_configuration(basic_config_class):
    """Test Meta class configuration"""
    config = basic_config_class()
    assert config._cache is True  # Test cache setting from Meta
    assert len(config._loaders) == 1  # Test loaders from Meta
