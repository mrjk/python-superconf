---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.16.7
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Field Types and Default/Unset Values

Welcome to the second SuperConf tutorial! In this guide, we'll explore the various field types available in SuperConf and how they handle default and unset values.

In the previous tutorial, we used the generic `Field` class for all our configuration values. While this works, SuperConf provides specialized field types that offer type validation and conversion, making your configuration more robust.

## Field Types Overview

SuperConf provides several specialized field types to handle different kinds of data:

- `FieldBool` - For boolean values with automatic string-to-boolean conversion
- `FieldString` - For string values, converting any input to strings
- `FieldInt` - For integer values, with automatic string-to-int conversion
- `FieldFloat` - For floating-point values
- `FieldDict` - For dictionary values
- `FieldList` - For list values
- `FieldTuple` - For tuple values
- `FieldOption` - For values restricted to a set of options (TODO)

Let's see how to use these field types in practice.

## Defining a Configuration with Various Field Types

First, let's create a configuration class that uses various field types:

```python
from superconf import ConfigurationObj
from superconf.fields import (
    Field,
    FieldBool, FieldString, FieldInt, FieldFloat, 
    FieldDict, FieldList, FieldTuple, FieldOption
)
from superconf.common import NOT_SET, NOT_SET_DICT, NOT_SET_LIST

class AppConfig(ConfigurationObj):
    """Configuration with various field types"""
    
    # Boolean fields with automatic conversion
    is_enabled = FieldBool(default=True)
    debug_mode = FieldBool(default="yes")  # Will be converted to True
    verbose_logs = FieldBool(default="off")  # Will be converted to False
    
    # String fields
    app_name = FieldString(default="MyApp")
    version = FieldString(default="1.0.0")
    
    # Numeric fields
    worker_count = FieldInt(default=4)
    timeout = FieldFloat(default=5.5)
    
    # Collection fields
    tags = FieldList(default=["web", "api"])
    settings = FieldDict(default={"theme": "dark"})
    dimensions = FieldTuple(default=(800, 600))
    
    # Fields with NOT_SET defaults
    unset = Field() # Equivalent of FieldString(default=NOT_SET)
    unset_string = FieldString() # Equivalent of FieldString(default=NOT_SET)
    unset_dict = FieldDict()     # Equivalent of FieldDict(default=NOT_SET_DICT)
    unset_list = FieldList()     # Equivalent of FieldList(default=NOT_SET_LIST)
    
# Create an instance with default values
app = AppConfig()

```

Now we created our instance, let's inspect it:

```python

# Print information about all fields
print("Configuration instance with specialized field types:")

# Print boolean fields
print("\nBoolean fields:")
print(f"is_enabled: {app.is_enabled} (type: {type(app.is_enabled).__name__})")
print(f"debug_mode: {app.debug_mode} (type: {type(app.debug_mode).__name__})")
print(f"verbose_logs: {app.verbose_logs} (type: {type(app.verbose_logs).__name__})")

# Print string fields
print("\nString fields:")
print(f"app_name: {app.app_name} (type: {type(app.app_name).__name__})")
print(f"version: {app.version} (type: {type(app.version).__name__})")

# Print numeric fields
print("\nNumeric fields:")
print(f"worker_count: {app.worker_count} (type: {type(app.worker_count).__name__})")
print(f"timeout: {app.timeout} (type: {type(app.timeout).__name__})")

# Print collection fields
print("\nCollection fields:")
print(f"tags: {app.tags} (type: {type(app.tags).__name__})")
print(f"settings: {app.settings} (type: {type(app.settings).__name__})")
print(f"dimensions: {app.dimensions} (type: {type(app.dimensions).__name__})")

# Print unset fields
print("\nUnset fields:")
print(f"unset: {app.unset} (type: {type(app.unset).__name__})")
print(f"unset_string: {app.unset_string} (type: {type(app.unset_string).__name__})")
print(f"unset_dict: {app.unset_dict} (type: {type(app.unset_dict).__name__})")
print(f"unset_list: {app.unset_list} (type: {type(app.unset_list).__name__})")
```

Notice how SuperConf automatically converts values to the correct type based on the field type. The most interesting example is `FieldBool`, which converts string values like "yes", "true", "on" to `True` and "no", "false", "off" to `False`.

## Default Values vs. Unset Values

SuperConf distinguishes between fields with default values and fields that are "unset." Let's understand the difference:

- A field with a default value will use that value when no override is provided
- A field with `NOT_SET` (or its variant) will remain "unset" until a value is provided

SuperConf provides special constants for unset values:

- `NOT_SET` - General unset value
- `NOT_SET_DICT` - Unset value for dictionary fields (empty dict)
- `NOT_SET_LIST` - Unset value for list fields (empty list)

Let's explore how these work in practice:

```python
from superconf.common import NOT_SET

# Create an instance with default values
app = AppConfig()

# Check if a field is NOT_SET
print("\nChecking for unset values:", app.unset)
print(id(app.unset), id(NOT_SET))
if app.unset is NOT_SET:
    print("unset is not set") # NEver executed since it's cast to string
else:
    print("unset has a value")

# Check if a field is NOT_SET
print("\nChecking for unset_string values:", app.unset_string)
print(id(app.unset_string), id(NOT_SET))
if app.unset_string is NOT_SET:
    print("unset_string is not set") # NEver executed since it's cast to string
else:
    print("unset_string has a value")

# NOT_SET_DICT ensures type safety by returning an empty dict
print(f"\nIs unset_dict an empty dict? {app.unset_dict == {}}")
print(f"unset_dict value: {app.unset_dict}")

# NOT_SET_LIST ensures type safety by returning an empty list
print(f"\nIs unset_list an empty list? {app.unset_list == []}")
print(f"unset_list value: {app.unset_list}")

# Set a value to a previously unset field
app.unset_string = "Now I have a value"
print(f"After setting: unset_string = {app.unset_string}")
```

There are other way to test values:

```python
assert app.unset_dict != NOT_SET
assert app.unset_dict == NOT_SET_DICT

# To test inherited values
assert isinstance(app.unset_dict, NOT_SET.type)
assert app.unset_dict is NOT_SET_DICT or app.unset_dict is NOT_SET
```

The advantage of using `NOT_SET` constants is that they maintain type safety. For example, `NOT_SET_DICT` behaves like an empty dictionary, so operations that expect a dictionary will still work.

## Type Conversion in Field Types

Each field type has its own type conversion behavior. Let's explore how type conversion works for different field types:

### FieldBool

`FieldBool` is particularly powerful as it can convert various string representations to boolean values:

```python
# Create a configuration class to demonstrate boolean conversion
class BoolConfig(ConfigurationObj):
    """Configuration for testing boolean conversion"""
    
    # These strings convert to True
    yes_value = FieldBool(default="yes")
    true_value = FieldBool(default="true")
    one_value = FieldBool(default="1")
    on_value = FieldBool(default="on")
    y_value = FieldBool(default="y")
    
    # These strings convert to False
    no_value = FieldBool(default="no")
    false_value = FieldBool(default="false")
    zero_value = FieldBool(default="0")
    off_value = FieldBool(default="off")
    n_value = FieldBool(default="n")

# Create an instance
bool_config = BoolConfig()

# Print the converted values
print("\nBoolean field conversion examples:")
print("Values converted to True:")
print(f"'yes' -> {bool_config.yes_value}")
print(f"'true' -> {bool_config.true_value}")
print(f"'1' -> {bool_config.one_value}")
print(f"'on' -> {bool_config.on_value}")
print(f"'y' -> {bool_config.y_value}")

print("\nValues converted to False:")
print(f"'no' -> {bool_config.no_value}")
print(f"'false' -> {bool_config.false_value}")
print(f"'0' -> {bool_config.zero_value}")
print(f"'off' -> {bool_config.off_value}")
print(f"'n' -> {bool_config.n_value}")

# Verify with assertions
assert bool_config.yes_value is True
assert bool_config.true_value is True
assert bool_config.one_value is True
assert bool_config.on_value is True
assert bool_config.y_value is True

assert bool_config.no_value is False
assert bool_config.false_value is False
assert bool_config.zero_value is False
assert bool_config.off_value is False
assert bool_config.n_value is False

print("\nAll boolean assertions passed!")
```

### Other Field Types Conversion

Other field types also perform appropriate conversions:

```python
# Create a configuration class to demonstrate other type conversions
class ConversionConfig(ConfigurationObj):
    """Configuration for testing type conversion"""
    
    # String conversion
    int_to_string = FieldString(default=123)
    bool_to_string = FieldString(default=True)
    none_to_string = FieldString(default=None)
    
    # Integer conversion
    string_to_int = FieldInt(default="42")
    float_to_int = FieldInt(default=3.14)
    bool_to_int = FieldInt(default=True)
    
    # Float conversion
    string_to_float = FieldFloat(default="3.14")
    int_to_float = FieldFloat(default=42)
    
    # List conversion
    string_to_list = FieldList(default="single item")

# Create an instance
conv_config = ConversionConfig()

# Print the converted values
print("\nOther field type conversion examples:")

print("\nString conversion:")
print(f"int(123) -> '{conv_config.int_to_string}'")
print(f"bool(True) -> '{conv_config.bool_to_string}'")
print(f"None -> '{conv_config.none_to_string}'")

print("\nInteger conversion:")
print(f"'42' -> {conv_config.string_to_int}")
print(f"3.14 -> {conv_config.float_to_int}")
print(f"True -> {conv_config.bool_to_int}")

print("\nFloat conversion:")
print(f"'3.14' -> {conv_config.string_to_float}")
print(f"42 -> {conv_config.int_to_float}")

print("\nList conversion:")
print(f"'single item' -> {conv_config.string_to_list}")

# Verify with assertions
assert conv_config.int_to_string == "123"
assert conv_config.bool_to_string == "True"
assert conv_config.none_to_string == "None"

assert conv_config.string_to_int == 42
assert conv_config.float_to_int == 3
assert conv_config.bool_to_int == 1

assert conv_config.string_to_float == 3.14
assert conv_config.int_to_float == 42.0

assert conv_config.string_to_list == ["single item"]

print("\nAll conversion assertions passed!")
```

## Iterating and Getting Length

A Configuration object acts like a dictionary in many ways. You can iterate over its fields and get its length:

```python
# Create a simple configuration for demonstration
class SimpleConfig(ConfigurationObj):
    field1 = FieldString(default="value1")
    field2 = FieldInt(default=42)
    field3 = FieldBool(default=True)

# Create an instance
simple_config = SimpleConfig()

# Get the number of fields
field_count = len(simple_config)
print(f"\nConfig has {field_count} fields")

# Iterate over fields
print("\nIterating over configuration fields:")
for name, field in simple_config.items():
    value = field.get_value()
    field_type = type(field).__name__
    print(f"Field '{name}' ({field_type}): {value}")
```

## Summary

In this guide, we've learned:

- The various field types available in SuperConf
- How to define fields with different types
- The difference between default values and unset values
- How type conversion works for different field types
- How to work with NOT_SET values
- How to iterate over configuration objects and get their length

Field types are a powerful feature of SuperConf that help ensure your configuration values are of the correct type. By using the appropriate field type, you can make your configuration more robust and easier to work with.

## Try It Yourself

Here are some exercises to practice what you've learned:

1. Create a configuration model for a database connection with appropriate field types for host, port, username, password, and connection timeout.
2. Experiment with `FieldBool` by creating a configuration with boolean fields and initializing them with various string values.
3. Create a configuration with a `FieldOption` that restricts a value to a set of valid options.
4. Try to set an invalid value to a field with a specific type and observe the error.
5. Create a configuration with `NOT_SET` values and check how they behave when accessed before and after setting a value. 
