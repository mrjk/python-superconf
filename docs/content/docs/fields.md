# Configuration Fields

SuperConf provides several built-in field types to handle different types of configuration values. Each field type is designed to handle specific data types and provides validation, type casting, and default value handling.

## Available Field Types

### FieldString
- Purpose: Handles text and string values
- Default: Empty string (`""`) if not specified
- Validation: Ensures the value is or can be converted to a string
- Common uses: Names, paths, URLs, text configurations

### FieldInt
- Purpose: Handles integer numeric values
- Default: `0` if not specified
- Validation: Ensures the value is or can be converted to an integer
- Common uses: Ports, counts, numeric IDs, timeouts

### FieldBool
- Purpose: Handles boolean (True/False) values
- Default: `False` if not specified
- Validation: Accepts boolean values, strings like "true"/"false", 0/1
- Common uses: Feature flags, toggles, enable/disable settings

### FieldList
- Purpose: Handles lists or arrays of values
- Default: Empty list (`[]`) if not specified
- Validation: Ensures the value is a sequence type
- Common uses: Multiple values, arrays of settings, feature lists

### FieldDict
- Purpose: Handles nested dictionary/object configurations
- Default: Empty dict (`{}`) if not specified
- Validation: Ensures the value is a mapping type
- Common uses: Nested configurations, complex settings groups

### FieldFloat
- Purpose: Handles floating-point decimal numbers
- Default: `0.0` if not specified
- Validation: Ensures the value is or can be converted to a float
- Common uses: Scientific calculations, percentages, rates

## Field Properties

Each field can have the following properties:

### Default Value
- Set using the `default` parameter
- Provides a fallback value if none is specified
- Must match the field type

### Help Text
- Set using the `help` parameter
- Provides documentation for the configuration option
- Used in generating documentation and error messages

### Validation
- Set using the `validators` parameter
- List of functions that validate the input
- Each validator should return True or raise ValidationError
- Custom validators can implement complex business rules

### Type Casting
- Automatic conversion of input values to the correct type
- Handles string inputs from config files
- Raises TypeError if conversion fails

## Example Usage

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList, FieldDict

class Config(Configuration):
    # String field with default and help
    name = FieldString(default="app", help="Application name")
    
    # Integer with validation
    port = FieldInt(
        default=8080,
        help="Server port",
        validators=[lambda x: 1024 <= x <= 65535]
    )
    
    # Boolean field
    debug = FieldBool(default=False, help="Enable debug mode")
    
    # List field with default values
    features = FieldList(default=["basic"], help="Enabled features")
    
    # Dictionary field with nested configuration
    database = FieldDict(default={
        "host": "localhost",
        "port": 5432
    }, help="Database configuration")
```

## Best Practices

1. Always provide help text for better documentation
2. Use appropriate validators to ensure data integrity
3. Set sensible default values when possible
4. Use type-specific fields instead of generic ones
5. Structure nested configurations using FieldDict
``` 