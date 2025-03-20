"""Unit tests for core Configuration functionality.

This module contains unit tests for the Configuration class, testing basic configuration
operations, field access, and configuration behavior.
"""

import pytest

from superconf.configuration import Configuration
from superconf.exceptions import UndeclaredField
from superconf.fields import Field

# Test data
EXAMPLE_DICT = {
    "item1": True,
    "item2": 4333,
}

FULL_CONFIG = {
    "field1": False,
    "field2": "Default value",
    "field3": 42,
    "field4": EXAMPLE_DICT,
}

OVERRIDE_CONFIG = {
    "field1": True,
    "field2": "Override value",
    "field3": 100,
}

EXTRA_CONFIG = {
    **FULL_CONFIG,
    "extra_field": "should not be allowed",
}


# Test fixtures
@pytest.fixture
def base_config_class():
    """Create a basic configuration class for testing."""

    class TestConfig(Configuration):
        """Test configuration class."""

        field1 = Field(default=False, help="Toggle debugging on/off.")
        field2 = Field(default="Default value", help="String field")
        field3 = Field(default=42, help="Integer field")
        field4 = Field(default=EXAMPLE_DICT, help="Dict field")

    return TestConfig


@pytest.fixture
def strict_config_class(base_config_class):
    """Create a strict configuration class that rejects extra fields."""

    class StrictConfig(base_config_class):
        """Strict configuration class."""

        class Meta:
            extra_fields = False

    return StrictConfig


@pytest.fixture
def flexible_config_class(base_config_class):
    """Create a configuration class that allows extra fields."""

    class FlexibleConfig(base_config_class):
        """Flexible configuration class."""

        class Meta:
            extra_fields = True

    return FlexibleConfig


@pytest.fixture
def meta_default_config_class(base_config_class):
    """Create a configuration class with Meta defaults."""

    class DefaultConfig(base_config_class):
        """Configuration with Meta defaults."""

        class Meta:
            default = {
                "field1": True,
                "field2": "Meta default value",
                "field3": 100,
            }

    return DefaultConfig


# Unit tests
def test_empty_config_uses_defaults(base_config_class):
    """Test that a configuration with no provided values uses field defaults."""
    config = base_config_class()

    assert config.field1 is False
    assert config.field2 == "Default value"
    assert config.field3 == 42
    assert config.field4 == EXAMPLE_DICT


def test_config_with_provided_values(base_config_class):
    """Test that provided values override field defaults."""
    config = base_config_class(value=OVERRIDE_CONFIG)

    assert config.field1 is True
    assert config.field2 == "Override value"
    assert config.field3 == 100
    assert config.field4 == EXAMPLE_DICT  # Not in OVERRIDE_CONFIG, so uses default


def test_meta_default_values(meta_default_config_class):
    """Test that Meta.default values override field defaults."""
    config = meta_default_config_class()

    assert config.field1 is True
    assert config.field2 == "Meta default value"
    assert config.field3 == 100
    assert config.field4 == EXAMPLE_DICT  # Not in Meta.default, so uses field default


def test_provided_values_override_meta_defaults(meta_default_config_class):
    """Test that provided values override Meta.default values."""
    override_values = {
        "field1": False,
        "field2": "Provided value",
    }
    config = meta_default_config_class(value=override_values)

    assert config.field1 is False
    assert config.field2 == "Provided value"
    assert config.field3 == 100  # From Meta.default
    assert config.field4 == EXAMPLE_DICT  # From field default


def test_attribute_and_item_access(base_config_class):
    """Test both attribute and dictionary-style access to config values."""
    config = base_config_class(value=FULL_CONFIG)

    # Test attribute access
    assert config.field1 is False
    assert config.field2 == "Default value"

    # Test dictionary-style access
    assert config["field1"] is False
    assert config["field2"] == "Default value"


def test_get_value_known_fields(base_config_class):
    """Test retrieval of known configuration values using get_value."""
    config = base_config_class(value=FULL_CONFIG)

    assert config.get_value("field1") is False
    assert config.get_value("field2") == "Default value"
    assert config.get_value("field3") == 42


def test_get_value_unknown_fields(base_config_class):
    """Test retrieval behavior for unknown configuration values."""
    config = base_config_class(value=FULL_CONFIG)

    # With default provided
    assert config.get_value("unknown_field", default="fallback") == "fallback"

    # Without default
    with pytest.raises(UndeclaredField):
        config.get_value("unknown_field")


def test_strict_config_rejects_extra_fields(strict_config_class):
    """Test that strict configuration rejects extra fields."""
    with pytest.raises(UndeclaredField):
        strict_config_class(value=EXTRA_CONFIG)


def test_flexible_config_allows_extra_fields(flexible_config_class):
    """Test that flexible configuration allows extra fields."""
    config = flexible_config_class(value=EXTRA_CONFIG)

    assert hasattr(config, "extra_field")
    assert config.extra_field == "should not be allowed"
    assert config["extra_field"] == "should not be allowed"


def test_immutable_object_behavior(base_config_class):
    """Test behavior with immutable objects (strings)."""
    config = base_config_class(value=FULL_CONFIG)

    # Same object should be returned for immutable types
    first_access = config.field2
    second_access = config.field2

    assert first_access is second_access
    assert first_access == "Default value"


def test_mutable_object_behavior(base_config_class):
    """Test behavior with mutable objects (dictionaries)."""
    config = base_config_class(value=FULL_CONFIG)

    # Objects should be the same for mutable types
    first_access = config.field4
    first_access_id = id(first_access)

    second_access = config.field4
    second_access_id = id(second_access)

    assert first_access_id == second_access_id
    assert first_access == EXAMPLE_DICT


def test_configuration_iteration(base_config_class):
    """Test iteration over configuration items."""
    config = base_config_class(value=FULL_CONFIG)

    items_count = 0
    collected_values = {}

    for name, item in config.items():
        items_count += 1
        collected_values[name] = config.get_value(name)

    assert items_count == len(FULL_CONFIG)
    assert collected_values == FULL_CONFIG
