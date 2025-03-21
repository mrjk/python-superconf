# Simplest Structure with SuperConf

Welcome to the first SuperConf tutorial! In this guide, we'll explore the fundamental building blocks of SuperConf and learn how to create and use simple configuration models.

SuperConf is a Python library that helps you manage application configuration in a structured, type-safe way. Unlike simple dictionary-based configurations, SuperConf provides a class-based approach with validation, type conversion, and hierarchical structures.

Let's start by understanding the basic components:

- `ConfigurationObj` - The main class for creating configuration models
- `Field` - Basic field definition for storing configuration values

## Defining a Configuration Model

The first step in using SuperConf is to define a configuration model. This is done by creating a class that inherits from `ConfigurationObj` and defining fields as class attributes.

Let's create a simple application configuration model:

```python
from superconf import ConfigurationObj, Field, NOT_SET

class AppConfig(ConfigurationObj):
    """Model with defaults values and help messages"""

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="A string field")
    field3 = Field(default=42, help="A numeric field")
    field4 = Field(default={"item1": True, "item2": 4333}, help="A dictionary field")
    field5 = Field(help="A field without defaults")
    field6 = Field(help="Another field without defaults")

# Let's print the class to see what we've created
print("Our configuration model:")
print(AppConfig)
```

When you run this code, you'll see the configuration class definition. Each field is defined with:
- A `default` value - The value used if no override is provided. If not provided, and not overrided, it will return a `NOT_SET` constant.
- A `help` message - Documentation for the field's purpose

This creates a blueprint for our configuration, but we haven't created an actual configuration instance yet.

## Creating and Using Configuration Instances

Now that we've defined our model, let's create instances and explore how to work with them.

### Creating an Instance With Default Values

The simplest way to create a configuration instance is without any arguments. We will see later how to inject configuration instead just using default values. This creates an instance with all default values:

```python
# Create an instance with default values
app = AppConfig()

# Let's print the instance
print("\nConfiguration instance with defaults:")
print(f"field1: {app.field1} (type: {type(app.field1).__name__})")
print(f"field2: {app.field2} (type: {type(app.field2).__name__})")
print(f"field3: {app.field3} (type: {type(app.field3).__name__})")
print(f"field4: {app.field4} (type: {type(app.field4).__name__})")
print(f"field5: {app.field5} (type: {type(app.field5).__name__})")

# We can verify the values match our defaults
assert app.field1 is False
assert app.field2 == "Default value"
assert app.field3 == 42
assert app.field4 == {"item1": True, "item2": 4333}
assert app.field5 is NOT_SET

print("\nAll default values are correctly set!")
```

Notice that each field has the correct value and type. SuperConf preserves the types of your default values.

There is a `get_value` method that can be used to show all fileds values:

```python
from pprint import pprint
pprint(app.get_value())
```


### Creating an Instance With Custom Values

In real applications, you'll usually want to override some or all of the default values. You can do this by providing a dictionary of values when creating the instance:

```python
# Define some custom configuration values
custom_config = {
    "field1": True,
    "field2": "Custom value",
    # "field3": 51, # We omit this field in way to illustrate how default values are handled
    "field4": {"custom": "dict"},
    "field5": "A string value"
}

# Create an instance with custom values
app = AppConfig(value=custom_config)

# Let's print the values
print("\nConfiguration instance with custom values:")
print(f"field1: {app.field1} (type: {type(app.field1).__name__})")
print(f"field2: {app.field2} (type: {type(app.field2).__name__})")
print(f"field3: {app.field3} (type: {type(app.field3).__name__}, from default config)")
print(f"field4: {app.field4} (type: {type(app.field4).__name__})")
print(f"field5: {app.field5} (type: {type(app.field5).__name__})")
print(f"field6: {app.field6} (type: {type(app.field6).__name__})")

# Verify the values match our custom configuration
assert app.field1 is True
assert app.field2 == "Custom value"
assert app.field3 == 42
assert app.field4 == {"custom": "dict"}
assert app.field5 == "A string value"

print("\nAll custom values are correctly set!")
```

As you can see, the values from `custom_config` have replaced the default values, but the structure of our configuration remains the same. As illustrated with `field3`, if a value is not set, then default value from model is used.

Once again, we can use `get_value` method to have a quick overview:

```python
pprint(app.get_value())
```


## Accessing Configuration Values

SuperConf provides multiple ways to access configuration values. This flexibility allows you to choose the approach that works best for your use case.

### 1. Using Attribute Access

The most straightforward way to access configuration values is through attribute access:

```python
# Direct attribute access - simple and intuitive
debug_enabled = app.field1
app_name = app.field2

print("\nAccessing values through attributes:")
print(f"debug_enabled: {debug_enabled}")
print(f"app_name: {app_name}")
```

This is the most Pythonic and readable way to access configuration values.

### 2. Using Dictionary-Style Access

You can also access values using dictionary-style access:

```python
# Dictionary-style access - useful when the field name is dynamic
debug_enabled = app["field1"]
app_name = app["field2"]

print("\nAccessing values through dictionary-style access:")
print(f"debug_enabled: {debug_enabled}")
print(f"app_name: {app_name}")

# This is particularly useful when the field name is in a variable
field_name = "field3"
value = app[field_name]
print(f"Dynamic access to {field_name}: {value}")
```

Dictionary-style access is especially useful when you need to access fields dynamically based on a variable.

### 3. Using the `get_value()` Method

The `get_value()` method is another way to access values:

```python
# Using get_value() method
debug_enabled = app.get_value("field1")
app_name = app.get_value("field2")

print("\nAccessing values through get_value():")
print(f"debug_enabled: {debug_enabled}")
print(f"app_name: {app_name}")
```

This method is particularly useful when you want to provide a fallback value if the field doesn't exist:

```python
# Get value for a NOT_SET field return NOT_SET
missing_value = app.get_value("field6")
print(f"Missing value without fallback: {missing_value}")

# Get value with a fallback for a non-existent field
missing_value = app.get_value("field6", "fallback")
print(f"Missing value with fallback: {missing_value}")

```

### 4. Accessing Field Objects

Sometimes you might need to access the field object itself, not just its value. This is useful when you need to access metadata about the field, like its default value or help text. There are two way to access a children, with by using `get_child()` method, or directly by using the call syntax:

```python
# Get the field object
field_obj = app("field1")
assert field_obj is app.get_child("field1")

# Then get its value
debug_enabled = field_obj.get_value()

# Or get its default value
default_value = field_obj.get_default()

# Or get its help text
help_text = field_obj.get_help()

print("\nAccessing field objects:")
print(f"Field value: {debug_enabled}")
print(f"Field default: {default_value}")
print(f"Field help: {help_text}")
```

The call syntax (`app("field1")` or `app.get_child("field1")`) always returns the field object, not the value.

## Handling Undefined Fields

One of the benefits of using SuperConf is that it provides clear errors when you try to access undefined fields. This helps catch configuration errors early.

Let's see what happens when we try to access fields that don't exist, with previsouly introduced methods:

```python
# Let's create a fresh instance
app = AppConfig()

print("\nTrying to access undefined fields:")

# Using attribute access raises AttributeError
try:
    value = app.undefined_field
    print("This should not print!")
except AttributeError as e:
    print(f"AttributeError: {e}")

# Using dictionary access raises KeyError
try:
    value = app["undefined_field"]
    print("This should not print!")
except KeyError as e:
    print(f"KeyError: {e}")

# Using get_value() raises UndeclaredField
try:
    from superconf import UndeclaredField
    value = app.get_value("undefined_field")
    print("This should not print!")
except UndeclaredField as e:
    print(f"UndeclaredField: {e}")
```

These errors help you catch typos or missing configuration fields early in development.

## Iterating Over Fields

A powerful feature of SuperConf is the ability to iterate over all fields in a configuration object. This is useful for introspection and generating documentation:

```python
# Create a configuration with default values
app = AppConfig()

print("\nIterating over all fields:")
for name, field_obj in app.items():
    value = field_obj.get_value()
    default = field_obj.get_default()
    help_text = getattr(field_obj, 'help', 'No help available')
    print(f"Field '{name}':")
    print(f"  - Value: {value}")
    print(f"  - Default: {default}")
    print(f"  - Help: {help_text}")
```

This makes it easy to inspect all fields in a configuration, which is useful for debugging or documenting.

## Setting Values

You can also set values after creating a configuration instance:

```python
# Create a configuration with default values
app = AppConfig()

print("\nBefore changing values:")
print(f"field1: {app.field1}")
print(f"field2: {app.field2}")

# Set new values
app.field1 = True
app.field2 = "New value"

print("\nAfter changing values:")
print(f"field1: {app.field1}")
print(f"field2: {app.field2}")

print("\nThis is updated from parent node as well:")
pprint(app.get_value())

assert False, "BUG HERE, missing __set__ dunder"

```

You can also set values using the dictionary syntax or the `set_value()` method:

```python
# Dictionary syntax
app["field3"] = 100

# set_value() method
app.set_value("field4", {"new": "dictionary"})

print("\nUsing alternative ways to set values:")
print(f"field3: {app.field3}")
print(f"field4: {app.field4}")
```

## Summary

In this guide, we've learned:

- How to define a basic configuration model using `ConfigurationObj` and `Field`
- How to create configuration instances with default and custom values
- Different ways to access configuration values
- How to handle undefined fields
- How to iterate over all fields in a configuration
- How to change configuration values

This provides the foundation for working with SuperConf. In the next guide, we'll explore different field types and how they handle default and unset values.

## Try It Yourself

Here are some exercises to practice what you've learned:

1. Create a configuration model for a web application with fields for `host`, `port`, `debug_mode`, and `database_url`.
2. Create an instance with default values and print all fields.
3. Create another instance with custom values and print all fields.
4. Try accessing a non-existent field and see what error you get.
5. Iterate over all fields and print their values and help text.

```python

```
