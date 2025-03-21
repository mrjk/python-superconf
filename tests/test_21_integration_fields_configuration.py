"""Integration tests for Fields and ConfigurationObj interaction.

This module tests how different Field types interact with the ConfigurationObj class,
including field validation, type casting, and complex field structures.
"""

import pytest

from superconf.configuration import ConfigurationObj
from superconf.exceptions import (
    CastValueFailure,
    InvalidCastConfiguration,
    InvalidField,
)
from superconf.fields import (
    Field,
    FieldBool,
    FieldConf,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldList,
    FieldString,
)

# Test data
NESTED_DICT = {
    "nested_key1": "nested_value1",
    "nested_key2": 42,
    "nested_list": [1, 2, 3],
}

CONFIG_WITH_VARIOUS_TYPES = {
    "string_field": "test string",
    "int_field": 42,
    "float_field": 3.14,
    "bool_field": True,
    "list_field": [1, 2, 3],
    "dict_field": NESTED_DICT,
}

INVALID_TYPES_CONFIG = {
    "string_field": 123,  # Should be string
    "int_field": "not an int",  # Should be int
    "float_field": "not a float",  # Should be float
    "bool_field": "not a bool",  # Should be bool
}


# Test fixtures
@pytest.fixture
def typed_config_class():
    """Fixture providing a configuration class with typed fields."""

    class TypedConfig(ConfigurationObj):
        """ConfigurationObj with strictly typed fields."""

        string_field = FieldString(default="default", help="String field")
        int_field = FieldInt(default=0, help="Integer field")
        float_field = FieldFloat(default=0.0, help="Float field")
        bool_field = FieldBool(default=False, help="Boolean field")
        list_field = FieldList(default=[], help="List field")
        dict_field = FieldDict(default={}, help="Dict field")

    return TypedConfig


@pytest.fixture
def validated_config_class():
    """Fixture providing a configuration class with specialized field types."""

    class SpecializedConfig(ConfigurationObj):
        """ConfigurationObj with specialized field types."""

        number = FieldInt(default=1, help="A number field")

        text = FieldString(default="test@example.com", help="A text field")

        option = Field(default="option1", help="An option field")

    return SpecializedConfig


@pytest.fixture
def nested_config_class():
    """Fixture providing a configuration class with nested configurations."""

    class DatabaseConfig(ConfigurationObj):
        """Database configuration section."""

        host = FieldString(default="localhost", help="Database host")
        port = FieldInt(default=5432, help="Database port")
        user = FieldString(default="admin", help="Database user")
        password = FieldString(default="password", help="Database password")

    class APIConfig(ConfigurationObj):
        """API configuration section."""

        enabled = FieldBool(default=True, help="Enable API")
        url = FieldString(default="/api", help="API base URL")
        version = FieldString(default="v1", help="API version")

    class AppConfig(ConfigurationObj):
        """Application configuration with nested configs."""

        debug = FieldBool(default=False, help="Debug mode")
        database = FieldConf(
            DatabaseConfig,
            default={},
            children_class=DatabaseConfig,
            help="Database configuration",
        )
        api = FieldConf(
            APIConfig, default={}, children_class=APIConfig, help="API configuration"
        )

    return AppConfig


# Integration tests
def test_field_type_casting(typed_config_class):
    """Test that fields properly cast values to their specified types."""
    # Create string representations that should be cast correctly
    castable_config = {
        "int_field": "42",  # String that should be cast to int
        "float_field": "3.14",  # String that should be cast to float
        "bool_field": "True",  # String that should be cast to bool
    }

    config = typed_config_class(value=castable_config)

    # Verify types after casting
    assert isinstance(config.int_field, int)
    assert config.int_field == 42

    assert isinstance(config.float_field, float)
    assert config.float_field == 3.14

    assert isinstance(config.bool_field, bool)
    assert config.bool_field is True


def test_invalid_type_handling(typed_config_class):
    """Test how invalid types are handled."""
    # Test each invalid type separately to pinpoint exact failures
    with pytest.raises(InvalidCastConfiguration):
        typed_config_class(value={"int_field": "not an int"})

    with pytest.raises(InvalidCastConfiguration):
        typed_config_class(value={"float_field": "not a float"})

    with pytest.raises(InvalidCastConfiguration):
        typed_config_class(value={"bool_field": "not a bool"})


def test_field_specialized_types(validated_config_class):
    """Test specialized field types functionality."""
    # Valid configuration
    valid_config = {"number": 42, "text": "user@example.com", "option": "option2"}

    config = validated_config_class(value=valid_config)

    assert config.number == 42
    assert config.text == "user@example.com"
    assert config.option == "option2"


def test_nested_configuration(nested_config_class):
    """Test nested configuration structures."""
    # Create a nested configuration
    nested_config_values = {
        "debug": True,
        "database": {
            "host": "db.example.com",
            "port": 5432,
            "user": "app_user",
            "password": "secure_password",
        },
        "api": {"enabled": True, "url": "/api/v2", "version": "v2"},
    }

    config = nested_config_class(value=nested_config_values)

    # Check top-level field
    assert config.debug is True

    # Check nested database config
    assert config.database.host == "db.example.com"
    assert config.database.port == 5432
    assert config.database.user == "app_user"
    assert config.database.password == "secure_password"

    # Check nested API config
    assert config.api.enabled is True
    assert config.api.url == "/api/v2"
    assert config.api.version == "v2"

    # Check dictionary access
    assert config["database"]["host"] == "db.example.com"
    assert config["api"]["url"] == "/api/v2"


def test_partial_nested_configuration(nested_config_class):
    """Test partial nested configuration with defaults filling in."""
    # Provide only some nested values
    partial_nested_values = {
        "database": {
            "host": "custom.example.com",
            # port, user, password not specified - should use defaults
        },
        "api": {
            "version": "v3"
            # enabled, url not specified - should use defaults
        },
    }

    config = nested_config_class(value=partial_nested_values)

    # Check top-level field (using default)
    assert config.debug is False

    # Check nested database config (mix of custom and defaults)
    assert config.database.host == "custom.example.com"
    assert config.database.port == 5432  # Default
    assert config.database.user == "admin"  # Default
    assert config.database.password == "password"  # Default

    # Check nested API config (mix of custom and defaults)
    assert config.api.enabled is True  # Default
    assert config.api.url == "/api"  # Default
    assert config.api.version == "v3"  # Custom


def test_nested_configuration_validation(nested_config_class):
    """Test validation in nested configurations."""
    # Create a config with an invalid port number (string instead of int)
    invalid_nested_values = {"database": {"port": "not_an_int"}}

    with pytest.raises(InvalidCastConfiguration):
        nested_config_class(value=invalid_nested_values)
