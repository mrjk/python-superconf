# Validation Architecture

<div align="center">
  <p><em>Understanding the design and internal workings of Superconf's validation architecture</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">🔍 Implementation</a> |
  <a href="03_type_casting.md">⏮️ Previous: Type Casting System</a> |
  <a href="05_configuration_loading.md">⏭️ Next: Configuration Loading</a>
</p>

---

This document explains the design and internal workings of Superconf's validation architecture.

## The Purpose of Validation

Validation in Superconf serves several important purposes:

1. **Type safety** - Ensuring configuration values have the correct data types
2. **Value constraints** - Verifying that values meet specific requirements (e.g., ranges, formats)
3. **Required fields** - Checking that all required fields have values
4. **Structural validation** - Validating the structure of complex configuration objects
5. **Business rules** - Enforcing application-specific business rules
6. **Error reporting** - Providing clear and helpful error messages

## Layered Validation Approach

Superconf implements a layered validation approach:

1. **Cast function validation** - Type conversion and basic value validation
2. **Field type validation** - Field-specific validation rules
3. **Container validation** - Validation of relationships between fields
4. **Custom validation** - Developer-defined validation rules

This layered approach allows for both standard type checking and complex business logic validation.

## Cast Function Validation

The first layer of validation occurs in the cast functions, which convert input values to the appropriate Python types:

```python
class AsInt(AbstractCast):
    def __call__(self, value):
        try:
            # Type conversion logic
            return int(value)
        except ValueError:
            raise InvalidCastConfiguration(f"Cannot convert to int: {value}")
```

Cast functions validate that:
- Values can be converted to the required type
- Values adhere to basic format requirements
- Values are within acceptable ranges

For more details on cast functions, see [Type Casting System](03_type_casting.md).

## Field Type Validation

The second layer of validation occurs in the field types, which can implement their own validation logic:

```python
class FieldPort(FieldInt):
    def __init__(self, default=MISSING, help=None, **kwargs):
        super().__init__(default=default, help=help, **kwargs)
    
    def validate(self, value):
        super().validate(value)  # First call parent validation
        
        # Then add field-specific validation
        if value < 1 or value > 65535:
            raise ValidationError(f"Port must be between 1 and 65535, got: {value}")
```

Field type validation can include:
- Range checks
- Format validation
- Pattern matching
- Enumeration validation

## Container Validation

The third layer of validation occurs in container types, which validate relationships between fields:

```python
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    username = FieldString()
    password = FieldString()
    
    def validate(self):
        super().validate()  # First call parent validation
        
        # Then add container-specific validation
        if self.host == "localhost" and self.port != 5432:
            raise ValidationError("When host is localhost, port must be 5432")
```

Container validation can include:
- Field interdependencies
- Conditional requirements
- Complex business rules
- High-level structural validation

## Custom Validation Methods

Superconf allows developers to define custom validation methods in their configuration classes:

```python
class ServerConfig(ContainerConf):
    host = FieldString(default="0.0.0.0")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    
    def validate(self):
        super().validate()  # Always call parent validation first
        
        # Custom validation logic
        if self.debug and self.host != "localhost":
            raise ValidationError("Debug mode can only be enabled on localhost")
```

Custom validation methods can implement any application-specific validation rules.

## Validation Triggers

Validation in Superconf can be triggered at several points:

1. **During initialization** - When a configuration instance is created
2. **During value setting** - When configuration values are modified
3. **Explicitly** - When the `validate()` method is called directly

This flexibility allows developers to choose when validation should occur based on their application's needs.

## Required Fields Validation

Superconf validates that all required fields (those without default values) have values:

```python
class UserConfig(ContainerConf):
    username = FieldString()  # Required (no default)
    password = FieldString()  # Required (no default)
    email = FieldString(default="")  # Optional (has default)
```

If a required field is not provided, Superconf raises a `MissingRequiredField` exception.

## Nested Configuration Validation

Validation cascades through nested configuration structures:

```python
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    username = FieldString()  # Required
    password = FieldString()  # Required

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    database = FieldConf(DatabaseConfig)
```

When `AppConfig` is validated, it also validates the `DatabaseConfig` instance in the `database` field.

## Exception Hierarchy

Superconf uses a hierarchy of exception classes for validation errors:

```
SuperconfException
├── ConfigurationException
│   ├── ValidationError
│   │   ├── MissingRequiredField
│   │   └── InvalidValue
│   └── InvalidCastConfiguration
└── ...
```

This hierarchy allows applications to catch specific types of validation errors or all validation errors.

## Error Messages

Superconf puts a strong emphasis on clear and helpful error messages:

```python
try:
    config = ServerConfig(port="not_a_number")
except InvalidCastConfiguration as e:
    print(f"Error: {e}")
    # Error: Cannot convert to int: not_a_number (field: port)
```

These error messages include:
- The nature of the error
- The problematic value
- The field name
- Context information when appropriate

## The FAIL Sentinel

Superconf uses a special `FAIL` sentinel value to trigger validation failures:

```python
class FieldPort(FieldInt):
    def __init__(self, default=MISSING, help=None, **kwargs):
        super().__init__(default=default, help=help, **kwargs)
        
    def validate(self, value):
        if value < 1 or value > 65535:
            return FAIL(f"Port must be between 1 and 65535, got: {value}")
        return value  # Valid
```

This approach allows validation methods to either return a valid value or signal a validation failure.

## Validation and Inheritance

Validation in Superconf works well with inheritance:

```python
class BaseConfig(ContainerConf):
    name = FieldString(default="Base")
    
    def validate(self):
        super().validate()
        # Base validation logic

class DerivedConfig(BaseConfig):
    version = FieldString(default="1.0.0")
    
    def validate(self):
        super().validate()  # Calls BaseConfig.validate()
        # Additional validation logic
```

This allows validation logic to be reused and extended through inheritance.

## Field-specific vs. Container-level Validation

Superconf distinguishes between two types of validation:

1. **Field-specific validation** - Validation that applies to a single field in isolation
2. **Container-level validation** - Validation that involves multiple fields and their relationships

This distinction allows for appropriate separation of concerns:

```python
# Field-specific validation
class FieldPort(FieldInt):
    def validate(self, value):
        if value < 1 or value > 65535:
            return FAIL(f"Port must be between 1 and 65535, got: {value}")
        return value

# Container-level validation
class ServerConfig(ContainerConf):
    host = FieldString(default="0.0.0.0")
    port = FieldPort(default=8000)
    
    def validate(self):
        super().validate()
        if self.host == "localhost" and self.port not in (8000, 8080):
            raise ValidationError("When host is localhost, port must be 8000 or 8080")
```

## Validation Extensibility

Superconf's validation architecture is designed to be extensible:

1. Custom field types can implement their own validation logic
2. Custom container types can implement complex validation rules
3. Application-specific validation can be added to configuration classes

This extensibility allows Superconf to handle a wide range of validation requirements.

## Conditional Validation

Superconf supports conditional validation through custom validation methods:

```python
class PaymentConfig(ContainerConf):
    method = FieldString(default="credit_card")
    credit_card_number = FieldString(default="")
    paypal_email = FieldString(default="")
    
    def validate(self):
        super().validate()
        
        if self.method == "credit_card" and not self.credit_card_number:
            raise ValidationError("Credit card number is required for credit card payments")
            
        if self.method == "paypal" and not self.paypal_email:
            raise ValidationError("PayPal email is required for PayPal payments")
```

This allows for flexible validation based on configuration values.

## Validation and Serialization

Validation in Superconf is closely integrated with serialization:

1. Validation ensures that configuration can be serialized to external formats
2. Deserialization triggers validation to ensure data integrity

This integration helps maintain consistency between in-memory configuration and serialized representations.

## Performance Considerations

Superconf's validation architecture is designed to balance thoroughness with performance:

- Validation is only performed when necessary
- Field-level validation is performed before more expensive container-level validation
- Validation results can be cached for repeated access

## Related How-To Guides

For practical applications of validation, see:

- [Creating Custom Field Types](../howto/03_custom_field_types.md) 