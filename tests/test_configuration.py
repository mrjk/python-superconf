import pytest
from superconf.configuration import (
    Configuration,
    Field,
    FieldConf,
    ConfigurationDict,
    ConfigurationList,
)
from superconf.fields import (
    as_boolean,
    as_int,
    as_list,
    as_dict,
    as_tuple,
    as_option,
    as_is,
)
from superconf.exceptions import (
    UnknownSetting,
    UnknownExtraField,
    UndeclaredField,
    CastValueFailure,
)
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

    class StrictConfig(ConfigurationDict):
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


def test_cast_functionality():
    """Test casting functionality in configuration"""

    class CastConfig(Configuration):
        field = Field(cast=as_int)

    # Test successful cast
    config = CastConfig()
    config.set_values({"field": 42})
    assert config.field == 42
    assert isinstance(config.field, int)

    # Test with string cast
    config.set_values({"field": "44"})
    assert config.field == 44
    assert isinstance(config.field, int)

    # Test cast returning None
    class NullCastConfig(Configuration):
        field = Field(cast=lambda x: None)

    config = NullCastConfig()
    config.set_values({"field": "value"})
    assert config.field is None


# def test_parent_configuration_query():
#     """Test querying parent configuration with various parameters"""

#     class ChildConfig(Configuration):
#         child_field = Field()

#     class ParentConfig(Configuration):
#         parent_field = FieldConf(
#             children_class=ChildConfig,
#             default={"child_field": "parent_value"})


#     parent = ParentConfig()
#     child = parent["parent_field"]
#     # child = ChildConfig(parent=parent)

#     # Test querying existing parent field
#     assert child.query_parent_cfg("children_class") == ChildConfig

#     # Test querying with as_subkey parameter
#     assert child.query_parent_cfg("default", as_subkey=True) == "parent_value"

#     # Test with cast parameter
#     assert child.query_parent_cfg("parent_field", cast=str) == "parent_value"


def test_dynamic_children_creation():
    """Test dynamic children creation in configuration"""

    class DynConfig(ConfigurationDict):
        meta__extra_fields = True

    config = DynConfig()
    config.set_values({"dynamic_field": {"nested": "value"}})

    assert isinstance(config["dynamic_field"], dict)
    assert config["dynamic_field"]["nested"] == "value"


def test_configuration_default_property():
    """Test the default property of configuration fields"""

    class DefaultConfig(Configuration):
        field = Field(default="test_default")

    config = DefaultConfig()
    assert config.field == "test_default"

    # Test accessing the default property directly
    field_instance = DefaultConfig.field
    assert field_instance.default == "test_default"


def test_configuration_cast_property():
    """Test the cast property of configuration fields"""

    def custom_cast(value):
        return f"casted_{value}"

    class CastConfig(Configuration):
        field = Field(cast=custom_cast)

    config = CastConfig()
    field_instance = CastConfig.field
    assert field_instance.cast == custom_cast

    config.set_values({"field": "test"})
    assert config.field == "casted_casted_test"


def test_configuration_list_operations():
    """Test various operations with ConfigurationList"""

    class CustomConfig(ConfigurationDict):
        field = Field(default="test")

    class ListConfig(ConfigurationList):
        meta__children_class = CustomConfig

    # Test list initialization with values
    config = ListConfig(value=[{"field": "value1"}, {"field": "value2"}])

    # Test iteration
    items = list(config.get_values(lvl=1))
    assert len(items) == 2
    assert all(isinstance(item, CustomConfig) for item in items)

    # Test get_values with different levels
    values = config.get_values(lvl=0)
    assert isinstance(values, ConfigurationList)
    assert len(values) == 2
    assert all(isinstance(v, CustomConfig) for v in values.get_values(lvl=1))


def test_configuration_dict_iteration():
    """Test iteration over ConfigurationDict"""

    class DictConfig(ConfigurationDict):
        field1 = Field(default="value1")
        field2 = Field(default="value2")

    config = DictConfig()
    items = list(config.get_values())
    assert len(items) == 2
    assert "field1" in items
    assert "field2" in items


def test_set_values_with_validation_strict():
    """Test setting values with validation in Configuration"""

    class ValidatedConfig(Configuration):

        meta__strict_cast = True
        field = Field(cast=int, default=23)

    config = ValidatedConfig()

    # Test with valid value
    config.set_values({"field": "42"})
    assert config["field"] == 42

    # Test with invalid value that can't be cast
    with pytest.raises(ValueError):
        config.set_values({"field": "not_an_int"})


def test_set_values_with_validation_not_strict():
    """Test setting values with validation in Configuration"""

    class ValidatedConfig(Configuration):

        meta__strict_cast = False
        field = Field(cast=int)

    config = ValidatedConfig()

    # Test with valid value
    config.set_values({"field": "42"})
    assert config["field"] == 42

    # Test with invalid value that can't be cast
    with pytest.raises(ValueError):
        config.set_values({"field": "not_an_int"})


def test_set_values_with_validation_strict_fail():
    """Test setting values with validation in Configuration"""

    class ValidatedConfig(Configuration):

        meta__strict_cast = True
        field = Field(cast=int)

    with pytest.raises(CastValueFailure):
        config = ValidatedConfig()

    # Test with valid value
    config = ValidatedConfig(value={"field": "777"})
    config.set_values({"field": "42"})
    assert config["field"] == 42

    # Test with invalid value that can't be cast
    with pytest.raises(ValueError):
        config.set_values({"field": "not_an_int"})


def test_nested_configuration_reset():
    """Test resetting nested configuration structures"""

    class NestedConfig(ConfigurationDict):
        meta__extra_fields = True
        meta__children_class = ConfigurationDict

    config = NestedConfig()
    config.set_values({"level1": {"level2": {"value": "test"}}})
    assert config["level1"]["level2"]["value"] == "test"
    config.reset()

    # After reset, accessing the value should create new empty configurations
    assert isinstance(config["level1"], ConfigurationDict)
    assert not hasattr(config["level1"], "level2")


def test_configuration_descriptor():
    """Test configuration field descriptor behavior"""

    class DescriptorConfig(Configuration):
        field = Field(default="test_value")

    # Test descriptor access on class
    assert isinstance(DescriptorConfig.field, Field)

    # Test descriptor access on instance
    config = DescriptorConfig()
    assert config.field == "test_value"


def test_special_meta_configurations():
    """Test configurations with special meta settings"""

    class SpecialConfig(ConfigurationDict):
        meta__strict_cast = True
        meta__extra_fields = False
        field = Field(cast=int)

    with pytest.raises(CastValueFailure):
        config = SpecialConfig()

    config = SpecialConfig(value={"field": "1333"})

    # Test strict casting
    with pytest.raises(ValueError):
        config.set_values({"field": "not_a_number"})

    # Test extra fields restriction
    with pytest.raises(UnknownExtraField):
        config.set_values({"unknown_field": "value"})


def test_configuration_hierarchy_with_values():
    """Test configuration hierarchy with value inheritance"""

    class ChildConfig(ConfigurationDict):
        child_field = Field(default="child_default")

    class ParentConfig(ConfigurationDict):
        meta__custom = "custom_value"
        parent_field = Field(default="parent_default")

    parent = ParentConfig()
    child = ChildConfig(parent=parent)
    grandchild = ChildConfig(parent=child)

    # Test hierarchy traversal
    hierarchy = grandchild.get_hierarchy()
    assert len(hierarchy) == 3
    assert hierarchy[0] == grandchild
    assert hierarchy[1] == child
    assert hierarchy[2] == parent

    # Test value inheritance
    assert child.query_parent_cfg("custom") == "custom_value"
    assert grandchild.query_parent_cfg("custom") == "custom_value"


def test_list_configuration_edge_cases():
    """Test edge cases in list configuration"""

    class ListConfig(ConfigurationList):
        meta__children_class = ConfigurationDict

    # Test empty list
    config = ListConfig(value=[])

    assert len(config) == 0
    assert config.get_values() == []

    # Test nested list values
    config = ListConfig(value=[{"nested": {"value": 1}}, {"nested": {"value": 2}}])

    values = config.get_values()
    assert len(values) == 2
    assert values[0]["nested"]["value"] == 1
    assert values[1]["nested"]["value"] == 2
