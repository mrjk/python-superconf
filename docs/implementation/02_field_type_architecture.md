# Field Type Architecture

<div align="center">
  <p><em>Understanding the design and internal workings of Superconf's field type system</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">🔍 Implementation</a> |
  <a href="01_configuration_principles.md">⏮️ Previous: Configuration Principles</a> |
  <a href="03_type_casting.md">⏭️ Next: Type Casting System</a>
</p>

---

This document explains the design and internal workings of Superconf's field type system.

## The Role of Field Types

Field types are at the core of Superconf's architecture. They serve several critical functions:

1. **Define structure** - Field types define what values are valid for a configuration field
2. **Provide type safety** - They ensure configuration values adhere to expected types
3. **Enable validation** - They validate that values meet specific requirements
4. **Document configuration** - They can include help text and other metadata
5. **Convert values** - They convert input values from various formats to the appropriate Python types

## Field Type Hierarchy

Superconf implements a hierarchical system of field types:

```
AbstractField
├── FieldLeaf - Base class for simple value fields
│   ├── FieldString
│   ├── FieldInt
│   ├── FieldFloat
│   ├── FieldBool
│   └── ...
├── FieldContainer - Base class for container fields
│   ├── FieldList
│   ├── FieldDict
│   ├── FieldTuple
│   └── ...
└── FieldConf - Field for nested configuration
```

This hierarchy allows for:

- Common functionality in base classes
- Specialized behavior in derived classes
- Consistent API across all field types
- Easy extension with custom field types

## Anatomy of a Field Type

Each field type in Superconf consists of several key components:

1. **Type definition** - The Python type this field represents
2. **Cast function** - A function to convert input values to the appropriate type
3. **Default value** - The value used when no value is provided
4. **Metadata** - Help text, labels, and other descriptive information
5. **Validation rules** - Rules that define valid values

Here's a simplified example of a field type implementation:

```python
class FieldInt(FieldLeaf):
    cast = AsInt()  # Cast function to convert values to integers
    
    def __init__(self, default=MISSING, help=None, **kwargs):
        self.default = default
        self.help = help
        # Additional initialization
```

## The Casting System

One of the most important components of the field type system is the casting mechanism, which converts input values to the appropriate Python type.

The casting system is designed to handle a wide range of input formats:

- String values from environment variables
- Native Python values from code
- JSON/YAML values from configuration files
- Command-line arguments

Each field type has an associated cast function that handles the conversion and validation:

```python
class AsInt(AbstractCast):
    def __call__(self, value):
        try:
            # Handle various input types
            if isinstance(value, bool):
                return 1 if value else 0
            if isinstance(value, (int, float)):
                return int(value)
            if isinstance(value, str):
                value = value.strip().lower()
                if value in ('yes', 'true', 'on'):
                    return 1
                if value in ('no', 'false', 'off'):
                    return 0
                return int(value)
            # Handle other types or raise appropriate errors
        except ValueError:
            raise InvalidCastConfiguration(f"Cannot convert to int: {value}")
```

For more details on the casting system, see [Type Casting System](03_type_casting.md).

## Field Type Lifecycle

The lifecycle of a field type in Superconf consists of several phases:

1. **Definition** - Field types are defined as class attributes in a `ContainerConf` subclass
2. **Initialization** - When the class is defined, fields are initialized with their default settings
3. **Class preparation** - Superconf processes the field definitions to prepare the configuration class
4. **Instance creation** - When a configuration instance is created, field values are set
5. **Value access** - When configuration values are accessed, fields may perform additional processing

This lifecycle allows Superconf to provide a clean API while handling complex internal logic.

## FieldLeaf vs. FieldContainer

Superconf distinguishes between two main categories of fields:

1. **FieldLeaf** - Fields that contain a single value (e.g., FieldString, FieldInt)
2. **FieldContainer** - Fields that contain multiple values (e.g., FieldList, FieldDict)

This distinction allows Superconf to:

- Apply different validation rules to different field types
- Handle nested structures efficiently
- Provide specialized behavior for container fields

## The FieldConf Type

The `FieldConf` type is special because it allows for nested configuration structures:

```python
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    username = FieldString()
    password = FieldString()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    database = FieldConf(DatabaseConfig)
```

This field type allows for:

- Complex configuration hierarchies
- Modular configuration design
- Reuse of configuration components
- Clear organization of related settings

## Field Type Extensions

Superconf is designed to be extended with custom field types. The extension mechanism allows developers to:

1. Create custom field types for specific data formats
2. Add specialized validation logic
3. Support complex data structures
4. Implement domain-specific configuration types

For practical examples of creating custom field types, see [Creating Custom Field Types](../howto/03_custom_field_types.md).

## Metadata and Introspection

Field types in Superconf include metadata that supports:

1. **Documentation generation** - Creating documentation from configuration definitions
2. **Schema generation** - Generating JSON Schema or other formats
3. **UI generation** - Building configuration UIs based on field types
4. **Validation messages** - Providing clear error messages

This metadata can be accessed through introspection, allowing for powerful tooling and integrations.

## Default Values and Required Fields

Superconf uses a special `MISSING` sentinel value to distinguish between:

1. Fields with explicit default values
2. Required fields (those without defaults)

This distinction enables Superconf to:

- Validate that required fields are provided
- Apply default values when needed
- Clearly communicate which fields are required

## Validation Architecture

Field types participate in Superconf's validation architecture:

1. **Type validation** - Ensuring values match the expected type
2. **Field-specific validation** - Applying rules specific to each field type
3. **Custom validation** - Supporting developer-defined validation rules

For more details on validation, see [Validation Architecture](04_validation_architecture.md).

## Field Types and Configuration Loading

The field type system is a crucial component of configuration loading:

1. Field types define how input values are processed
2. Field types provide validation during loading
3. Field type metadata guides the loading process

For more details on how configuration loading works with field types, see [Configuration Loading](05_configuration_loading.md).

## Performance Considerations

The field type system is designed for both flexibility and performance:

- Field type processing happens primarily during class definition
- Instance creation is optimized for speed
- Value access is direct when possible
- Validation is efficient and focused

This design ensures that Superconf remains performant even with complex configuration structures.

## Related How-To Guides

For practical applications of field types, see:

- [Creating Custom Field Types](../howto/03_custom_field_types.md) 