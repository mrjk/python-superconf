"""Unit tests for basic Configuration functionality."""

from pprint import pprint

import pytest

import superconf.exceptions
from superconf.configuration import Configuration
from superconf.fields import Field

EXAMPLE_DICT = {
    "item1": True,
    "item2": 4333,
}

FULL_CONFIG = {
    "field1": False,
    "field2": "Default value",
    "field3": 42,
    "field4": EXAMPLE_DICT,
    "field5": EXAMPLE_DICT,
}

EXTRA_CONFIG = {
    **FULL_CONFIG,
    "extra_field": "should not be allowed",
}

OVERRIDE_CONFIG = {
    "field1": True,  # Changed from False
    "field2": "Override value",  # Changed from "Default value"
    "field3": 100,  # Changed from 42
}


class BaseAppConfig(Configuration):
    """Base configuration class for tests."""

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="Another field")
    field3 = Field(default=42, help="Another field")
    field4 = Field(default=EXAMPLE_DICT, help="Another dict field")
    field5 = Field(default=EXAMPLE_DICT, help="Another dict field")


class DefaultAppConfig(BaseAppConfig):
    """Configuration with default Meta settings."""

    pass


class StrictAppConfig(BaseAppConfig):
    """Configuration with strict settings."""

    class Meta:
        allow_undeclared = False


class AllowExtraAppConfig(BaseAppConfig):
    """Configuration allowing extra fields."""

    class Meta:
        allow_undeclared = True


class DefaultValueConfig(BaseAppConfig):
    """Configuration with Meta.default values."""

    class Meta:
        default = {
            "field1": True,
            "field2": "Meta default value",
            "field3": 100,
        }


@pytest.fixture
def empty_config():
    """Fixture providing an empty configuration instance."""
    return DefaultAppConfig()


@pytest.fixture
def full_config():
    """Fixture providing a configuration instance with values."""
    return DefaultAppConfig(value=FULL_CONFIG)


@pytest.fixture
def strict_config():
    """Fixture providing a strict configuration instance."""
    return StrictAppConfig(value=FULL_CONFIG)


@pytest.fixture
def allow_extra_config():
    """Fixture providing a configuration that allows extra fields."""
    return AllowExtraAppConfig(value=FULL_CONFIG)


@pytest.fixture
def meta_default_config():
    """Fixture providing a configuration with Meta.default values."""
    return DefaultValueConfig()


def test_empty_config_defaults(empty_config):
    """Test configuration instantiated with no values uses defaults."""
    assert empty_config.field1 is False
    assert empty_config.field2 == "Default value"
    assert empty_config.field3 == 42
    assert empty_config.field4 == EXAMPLE_DICT
    assert empty_config.field5 == EXAMPLE_DICT


def test_full_config_values(full_config):
    """Test configuration instantiated with values."""
    assert full_config.field1 is False
    assert full_config.field2 == "Default value"
    assert full_config.field3 == 42
    assert full_config.field4 == EXAMPLE_DICT
    assert full_config.field5 == EXAMPLE_DICT


def test_meta_default_values(meta_default_config):
    """Test Meta.default values override field defaults."""
    assert meta_default_config.field1 is True  # From Meta.default
    assert meta_default_config.field2 == "Meta default value"  # From Meta.default
    assert meta_default_config.field3 == 100  # From Meta.default
    assert meta_default_config.field4 == EXAMPLE_DICT  # From field default
    assert meta_default_config.field5 == EXAMPLE_DICT  # From field default


def test_value_overrides_meta_default():
    """Test that provided values override Meta.default values."""
    config = DefaultValueConfig(value=OVERRIDE_CONFIG)
    assert config.field1 is True  # From OVERRIDE_CONFIG

    # print("===========")
    # pprint(config.__dict__)
    # pprint(config.__children__["field2"].__dict__)

    assert config.field2 == "Override value"  # From OVERRIDE_CONFIG
    assert config.field3 == 100  # From OVERRIDE_CONFIG
    assert config.field4 == EXAMPLE_DICT  # From field default
    assert config.field5 == EXAMPLE_DICT  # From field default


def test_attribute_and_item_access(full_config):
    """Test both attribute and dictionary-style access to config values."""
    assert full_config.field1 is False
    assert isinstance(full_config.field1, bool)
    assert full_config["field1"] is False
    assert isinstance(full_config["field1"], bool)


def test_known_value_retrieval(full_config):
    """Test retrieval of known configuration values."""
    assert full_config.get_value("field2") == "Default value"
    assert full_config.get_value("field3") == 42


def test_unknown_value_retrieval(full_config):
    """Test retrieval behavior for unknown configuration values."""
    assert full_config.get_value("tutu", default="SUPER") == "SUPER"

    with pytest.raises(superconf.exceptions.UndeclaredField):
        full_config.get_value("toto")


def test_immutable_object_behavior(full_config):
    """Test behavior with immutable objects (strings)."""
    assert isinstance(full_config.field2, str)
    # Same object should be returned for immutable types
    assert full_config.field2 is full_config.field2
    assert full_config.field2 == "Default value"


def test_mutable_object_behavior(full_config):
    """Test behavior with mutable objects (dictionaries)."""
    assert isinstance(full_config.field5, dict)
    # Objects should be equal but not identical
    assert full_config.field5 == EXAMPLE_DICT
    assert full_config.field5 is not EXAMPLE_DICT

    # Test dictionary immutability
    original = full_config.field5.copy()
    full_config.field5["new_key"] = "new_value"
    next_access = full_config.field5
    assert (
        next_access == original
    ), "Mutable objects should return a new copy on each access"


def test_iteration_and_values(full_config):
    """Test iteration over configuration items and value consistency."""
    collected_config = {}
    item_count = 0

    for name, item in full_config.items():
        item_count += 1
        collected_config[name] = full_config.get_value(
            item.key, default=item.get_default()
        )

    assert item_count == len(FULL_CONFIG)
    assert collected_config == FULL_CONFIG
    assert collected_config is not FULL_CONFIG


def test_extra_fields_behavior_strict():
    """Test strict configuration rejects extra fields."""
    with pytest.raises(superconf.exceptions.UndeclaredField):
        StrictAppConfig(value=EXTRA_CONFIG)


def test_extra_fields_behavior_default():
    """Test default configuration rejects extra fields."""
    with pytest.raises(superconf.exceptions.UndeclaredField):
        DefaultAppConfig(value=EXTRA_CONFIG)


def test_extra_fields_behavior_allow():
    """Test configuration allows extra fields when configured."""
    config = AllowExtraAppConfig(value=EXTRA_CONFIG)
    assert hasattr(config, "extra_field")
    assert config.extra_field == "should not be allowed"
    assert config["extra_field"] == "should not be allowed"
