import pytest
from superconf.configuration import (
    Configuration,
    Field,
    ConfigurationDict,
    ConfigurationList,
    FieldConf,
)
from superconf.exceptions import UnknownSetting, UnknownExtraField, UndeclaredField
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


def test_query_parent_cfg_no_parent():
    """Test querying parent configuration when no parent exists"""
    config = Configuration()
    with pytest.raises(UnknownSetting):
        config.query_parent_cfg("test_setting")

    # Test with default value
    assert (
        config.query_parent_cfg("test_setting", default="default_value")
        == "default_value"
    )


def test_configuration_list():
    """Test ConfigurationList functionality"""

    class ListConfig(ConfigurationList):
        meta__children_class = ConfigurationDict

    config = ListConfig(value=[{"key": "value1"}, {"key": "value2"}])
    assert config[0]["key"] == "value1"
    assert config[1]["key"] == "value2"

    # Test get_values for list
    values = config.get_values()
    assert isinstance(values, list)
    assert len(values) == 2


def test_extra_fields_disabled():
    """Test behavior when extra fields are disabled"""

    class StrictConfig(Configuration):
        meta__extra_fields = False
        field1 = Field()

    config = StrictConfig()

    # Should raise exception when trying to set undeclared field
    with pytest.raises(UnknownExtraField):
        config.set_values({"field1": "value1", "undeclared_field": "value2"})


def test_get_field_value_undeclared():
    """Test getting value for undeclared field"""
    config = ConfigurationDict()

    # Test with default value
    assert config.get_field_value(key="unknown", default="default") == "default"

    # Test without default value
    with pytest.raises(UndeclaredField):
        config.get_field_value(key="unknown")


def test_configuration_reset():
    """Test configuration reset functionality"""
    config = ConfigurationDict()
    config._cached_values = {"test": "value"}
    config.reset()
    assert not config._cached_values


def test_configuration_hierarchy():
    """Test getting configuration hierarchy"""
    parent = ConfigurationDict()
    child = ConfigurationDict(parent=parent)
    grandchild = ConfigurationDict(parent=child)

    hierarchy = grandchild.get_hierarchy()
    assert len(hierarchy) == 3
    assert hierarchy[0] == grandchild
    assert hierarchy[1] == child
    assert hierarchy[2] == parent


def test_invalid_field_key():
    """Test declaring a field with mismatched key"""
    with pytest.raises(AttributeError):

        class InvalidConfig(Configuration):
            field1 = Field(key="different_key")


def test_nested_configuration_with_cast():
    """Test nested configuration with type casting"""

    class NestedConfig(ConfigurationDict):
        meta__cast = dict
        meta__strict_cast = True

    config = NestedConfig(value={"key": "value"})
    assert isinstance(config.get_values(), dict)

    # Test empty value with cast
    empty_config = NestedConfig(value=None)
    assert isinstance(empty_config.get_values(), dict)


def test_configuration_iteration():
    """Test iteration over configuration dictionary"""

    class TestConfig(Configuration):
        field1 = Field(default="value1")
        field2 = Field(default="value2")

    config = TestConfig()
    # pprint (config.__dict__)

    items = list(config)
    assert len(items) == 2
    assert all(isinstance(k, str) and isinstance(v, Field) for k, v in items)


def test_configuration_dict_iteration():
    """Test iteration over configuration dictionary"""

    class TestConfig(ConfigurationDict):
        "Empty"

    config = TestConfig(value={"field1": "value1", "field2": "value2"})

    items = list(config)
    assert len(items) == 2
    assert all(isinstance(k, str) and isinstance(v, Field) for k, v in items)


def test_container_field_creation():
    """Test creation of container fields"""

    class ContainerConfig(Configuration):
        container = FieldConf(children_class=ConfigurationDict)

    config = ContainerConfig(value={"container": {"nested": "value"}})
    assert isinstance(config.container, ConfigurationDict)
    assert config.container.get_value("nested") == "value"


def test_container_dict_field_creation():
    """Test creation of container fields"""

    class ContainerConfig(ConfigurationDict):
        container = FieldConf(children_class=ConfigurationDict)

    config = ContainerConfig(value={"container": {"nested": "value"}})
    pprint(config.__dict__)
    assert isinstance(config.container, ConfigurationDict)
    assert config.container.get_value("nested") == "value"


def test_sequence_value_handling():
    """Test handling of sequence values in configuration"""
    class SeqConfig(ConfigurationDict):
        seq_field = Field(default=[1, 2, 3])

    config = SeqConfig()
    value = config.get_field_value("seq_field")
    assert isinstance(value, list)
    assert value == [1, 2, 3]
