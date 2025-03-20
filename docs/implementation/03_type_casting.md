# Type Casting System

<div align="center">
  <p><em>Understanding the architecture and internal workings of Superconf's type casting system</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">🔍 Implementation</a> |
  <a href="02_field_type_architecture.md">⏮️ Previous: Field Type Architecture</a> |
  <a href="04_validation_architecture.md">⏭️ Next: Validation Architecture</a>
</p>

---

This document explains the architecture and internal workings of Superconf's type casting system.

## The Purpose of Type Casting

The type casting system in Superconf serves several critical purposes:

1. **Type conversion** - Converting values from various input formats to the appropriate Python types
2. **Data normalization** - Standardizing input values to a consistent format
3. **Input validation** - Ensuring input values can be converted to the required type
4. **Default value handling** - Managing default values for configuration fields
5. **Error reporting** - Providing clear error messages when type conversion fails

## Architecture Overview

The casting system is built around the `AbstractCast` class, which defines the interface for all cast functions:

```python
class AbstractCast:
    def __call__(self, value):
        """Convert the value to the appropriate type."""
        raise NotImplementedError("Cast functions must implement __call__")
```

Each field type in Superconf is associated with a specific cast function that knows how to convert values to the appropriate type:

```python
class FieldString(FieldLeaf):
    cast = AsString()

class FieldInt(FieldLeaf):
    cast = AsInt()

class FieldBool(FieldLeaf):
    cast = AsBool()
```

## The Casting Process

When a value is set for a configuration field, it goes through the following process:

1. The field's cast function is called with the input value
2. The cast function attempts to convert the value to the appropriate type
3. If successful, the converted value is stored
4. If conversion fails, an `InvalidCastConfiguration` exception is raised

This process ensures that all values stored in a configuration instance are of the correct type.

## Built-in Cast Functions

Superconf includes several built-in cast functions for common data types:

| Cast Function | Purpose |
|---------------|---------|
| `AsString`    | Converts values to strings |
| `AsInt`       | Converts values to integers |
| `AsBool`      | Converts values to booleans |
| `AsFloat`     | Converts values to floating-point numbers |
| `AsList`      | Converts values to lists |
| `AsDict`      | Converts values to dictionaries |
| `AsTuple`     | Converts values to tuples |

Each of these cast functions is designed to handle a wide range of input formats.

## Type Coercion Rules

The casting system follows specific rules for type coercion:

### String Conversion

The `AsString` cast function handles:
- Native Python strings
- Numbers (converted to string representation)
- Booleans (converted to "true" or "false")
- None (converted to an empty string)
- Objects with a `__str__` method

### Integer Conversion

The `AsInt` cast function handles:
- Native Python integers
- Floating-point numbers (truncated to integers)
- Strings containing numeric values
- Booleans (True becomes 1, False becomes 0)
- Strings like "yes", "true", "on" (become 1)
- Strings like "no", "false", "off" (become 0)

### Boolean Conversion

The `AsBool` cast function handles:
- Native Python booleans
- Integers (0 is False, everything else is True)
- Strings like "yes", "true", "on", "1" (become True)
- Strings like "no", "false", "off", "0" (become False)
- Empty strings (become False)

### List Conversion

The `AsList` cast function handles:
- Native Python lists
- Tuples (converted to lists)
- Strings (split into lists based on a delimiter)
- Dictionaries (converted to lists of key-value pairs)
- Scalar values (wrapped in a list)

## Complex Cast Functions

For more complex data types, Superconf provides specialized cast functions:

### AsList with Element Casting

The `AsList` cast function can be configured to cast each element of the list:

```python
class AsIntList(AsList):
    def __init__(self, delimiter=","):
        self.delimiter = delimiter
        self.element_cast = AsInt()
    
    def __call__(self, value):
        items = super().__call__(value)
        return [self.element_cast(item) for item in items]
```

### AsDict with Key and Value Casting

The `AsDict` cast function can be configured to cast keys and values:

```python
class AsStringDict(AsDict):
    def __init__(self):
        self.key_cast = AsString()
        self.value_cast = AsString()
    
    def __call__(self, value):
        data = super().__call__(value)
        return {self.key_cast(k): self.value_cast(v) for k, v in data.items()}
```

## Nested Configuration Casting

The `FieldConf` type uses a special cast function that creates an instance of a nested configuration class:

```python
class AsConf(AbstractCast):
    def __init__(self, conf_class):
        self.conf_class = conf_class
    
    def __call__(self, value):
        if isinstance(value, self.conf_class):
            return value
        if isinstance(value, dict):
            return self.conf_class(**value)
        raise InvalidCastConfiguration(
            f"Cannot convert {value} to {self.conf_class.__name__}"
        )
```

This allows for recursive configuration structures.

## Error Handling

When a cast function fails to convert a value, it raises an `InvalidCastConfiguration` exception with a detailed error message:

```python
try:
    int_value = AsInt()("not_a_number")
except InvalidCastConfiguration as e:
    print(f"Error: {e}")  # Error: Cannot convert to int: not_a_number
```

These error messages are designed to help users quickly identify and fix configuration issues.

## Default Value Handling

The casting system also handles default values for configuration fields:

```python
class FieldInt(FieldLeaf):
    cast = AsInt()
    
    def __init__(self, default=MISSING, help=None, **kwargs):
        self.default = default
        self.help = help
        # Additional initialization
```

When a default value is provided, it is cast using the field's cast function to ensure it is of the correct type.

## Custom Cast Functions

Superconf allows developers to create custom cast functions for specialized needs:

```python
class AsEmail(AbstractCast):
    def __call__(self, value):
        value = str(value)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise InvalidCastConfiguration(f"Invalid email format: {value}")
        return value

class FieldEmail(FieldLeaf):
    cast = AsEmail()
```

This extensibility allows Superconf to handle a wide range of data types and validation requirements.

For more examples of custom cast functions, see [Creating Custom Field Types](../howto/03_custom_field_types.md).

## The MISSING Sentinel

Superconf uses a special `MISSING` sentinel value to distinguish between:

1. Values that were explicitly set to None
2. Values that were not set at all

This distinction is important for handling default values and required fields.

## Cast Function Composition

Cast functions can be composed to create more complex type conversion logic:

```python
class AsIntRange(AbstractCast):
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
        self.int_cast = AsInt()
    
    def __call__(self, value):
        value = self.int_cast(value)  # First cast to int
        
        # Then apply range validation
        if self.min_value is not None and value < self.min_value:
            raise InvalidCastConfiguration(
                f"Value {value} is less than minimum {self.min_value}"
            )
        if self.max_value is not None and value > self.max_value:
            raise InvalidCastConfiguration(
                f"Value {value} is greater than maximum {self.max_value}"
            )
        
        return value
```

This composition allows for powerful and flexible type conversion.

## Cast Function Parameters

Cast functions can be parameterized to customize their behavior:

```python
class AsList(AbstractCast):
    def __init__(self, delimiter=","):
        self.delimiter = delimiter
    
    def __call__(self, value):
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return value.split(self.delimiter)
        # Handle other types
```

This parameterization allows cast functions to be reused in different contexts.

## Integration with Validation

The casting system is integrated with Superconf's validation architecture:

1. Cast functions perform type validation
2. Field types apply additional validation
3. Container types validate relationships between fields

This integration ensures that configuration values are both well-typed and valid.

## Performance Considerations

The casting system is designed for both flexibility and performance:

- Cast functions are reused across configuration instances
- Common cases are optimized for speed
- Error handling is focused on clarity without sacrificing performance

## Related How-To Guides

For practical applications of the casting system, see:

- [Creating Custom Field Types](../howto/03_custom_field_types.md) 