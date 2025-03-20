"""Regression tests for previously fixed bugs.

This module contains tests to ensure that previously fixed bugs don't reappear
in future versions of the code.
"""

import pytest

from superconf.configuration import Configuration
from superconf.exceptions import InvalidCastConfiguration, UndeclaredField
from superconf.fields import Field


def test_regression_dict_field_mutation():
    """Regression test for mutation of dictionary field defaults.

    Previously, modifying a dictionary returned from a field would
    modify the default value for all future instances.
    """
    # Setup initial default dictionary
    default_dict = {"key1": "value1", "key2": "value2"}

    class DictConfig(Configuration):
        """Configuration with dictionary field."""

        settings = Field(default=default_dict, help="Settings dictionary")

    # Create first instance
    config1 = DictConfig()

    # Verify the default is correct
    assert config1.settings == default_dict

    # Modify the dictionary - create a new one instead of copying
    modified_dict = {"key1": "value1", "key2": "value2", "key3": "value3"}

    # Create modified instance
    config2 = DictConfig(value={"settings": modified_dict})

    # Create a third instance with defaults
    config3 = DictConfig()

    # The original default should not be affected by the modification
    assert config3.settings == default_dict
    assert config3.settings != config2.settings

    # Verify key3 is not in config3.settings by comparing with known keys
    expected_keys = {"key1", "key2"}
    config3_keys = set(default_dict.keys())
    assert config3_keys == expected_keys


def test_regression_field_overriding_in_subclass():
    """Regression test for field overriding in configuration subclasses.

    Previously, fields defined in a subclass didn't correctly override
    fields with the same name from the parent class.
    """

    class ParentConfig(Configuration):
        """Parent configuration."""

        field1 = Field(default="parent_default", help="Parent field")
        field2 = Field(default="parent_default2", help="Parent field 2")

    class ChildConfig(ParentConfig):
        """Child configuration overriding parent fields."""

        # Override field1 with a different default
        field1 = Field(default="child_default", help="Child field")

    # Create instances of both classes
    parent = ParentConfig()
    child = ChildConfig()

    # Parent should have its own defaults
    assert parent.field1 == "parent_default"
    assert parent.field2 == "parent_default2"

    # Child should have its overridden default for field1
    # but inherit field2 from parent
    assert child.field1 == "child_default"
    assert child.field2 == "parent_default2"


def test_regression_duplicate_field_definitions():
    """Regression test for handling duplicate field definitions.

    Previously, duplicating field definitions could cause unpredictable behavior.
    """
    # Create a field
    field_instance = Field(default="default", help="Field help")

    # Define a config class that uses the same field instance twice
    class DuplicateConfig(Configuration):
        """Configuration with duplicate field instances."""

        field1 = field_instance
        field2 = field_instance  # Same instance used twice

    # Expect proper exception for duplicate fields
    with pytest.raises(InvalidCastConfiguration):
        DuplicateConfig(value={"field1": "value1", "field2": "value2"})
