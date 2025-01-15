# Casts

SuperConf provides several built-in cast types to convert configuration values into appropriate Python types. These casts ensure that your configuration values are properly typed and validated.

## Available Casts

### AsBoolean (FieldBool)

Converts values to boolean type. Recognizes various string representations of true/false values.

**True values:**
- "1"
- "true", "True"
- "yes", "y"
- "on"
- "t"

**False values:**
- "0"
- "false", "False"
- "no", "n"
- "off"
- "f"

Example:
```python
from superconf import Configuration
from superconf.fields import FieldBool

class AppConfig(Configuration):
    debug = FieldBool(default=False)
    is_enabled = FieldBool(default="yes")
```

### AsInt (FieldInt)

Converts values to integer type. Raises `InvalidCastConfiguration` if the value cannot be converted to an integer.

Example:
```python
from superconf import Configuration
from superconf.fields import FieldInt

class AppConfig(Configuration):
    port = FieldInt(default=8080)
    max_connections = FieldInt(default="100")  # Will be converted to int
```

### AsList (FieldList)

Converts values to Python lists. Can handle:
- Empty values (returns empty list)
- String input (splits by delimiter, default is comma)
- Existing sequences (lists, tuples)
- Quoted strings with delimiters

Example:
```python
from superconf import Configuration
from superconf.fields import FieldList

class AppConfig(Configuration):
    plugins = FieldList(default=[])
    hosts = FieldList(default="localhost,127.0.0.1")  # Will become ["localhost", "127.0.0.1"]
    items = FieldList(default='"item,with,comma",simple')  # Will handle quoted items with commas
```

### AsTuple (FieldTuple)

Similar to AsList but converts values to Python tuples. Has the same parsing capabilities as AsList.

Example:
```python
from superconf import Configuration
from superconf.fields import FieldTuple

class AppConfig(Configuration):
    allowed_hosts = FieldTuple(default=("localhost",))
    ports = FieldTuple(default="8080,8081,8082")  # Will become ("8080", "8081", "8082")
```

### AsDict (FieldDict)

Converts values to Python dictionaries. Currently supports:
- Empty values (returns empty dict)
- Existing dictionary objects
- Note: String parsing is not implemented yet

Example:
```python
from superconf import Configuration
from superconf.fields import FieldDict

class AppConfig(Configuration):
    settings = FieldDict(default={})
    database = FieldDict(default={"host": "localhost", "port": 5432})
```

### AsOption (FieldOption)

Provides a way to map input values to predefined options. Useful for configuration values that should be one of a set of allowed values.

Features:
- Mapping of input values to predefined options
- Optional default option when invalid value is provided
- Raises `InvalidCastConfiguration` if no default and value is invalid

Example:
```python
from superconf import Configuration
from superconf.fields import FieldOption

options = {
    "_default_": "development",
    "dev": "development",
    "prod": "production",
    "test": "testing"
}

class AppConfig(Configuration):
    environment = FieldOption(options, default="dev")
    mode = FieldOption(options, default_option="_default_")  # Falls back to default option
```

### AsIdentity (No Field Type)

This is a no-op cast that returns the value as-is. Used internally when no specific casting is needed.

## String Field (FieldString)

While not a cast in the traditional sense, the FieldString ensures values are converted to strings.

Example:
```python
from superconf import Configuration
from superconf.fields import FieldString

class AppConfig(Configuration):
    name = FieldString(default="app")
    version = FieldString(default=1.0)  # Will be converted to "1.0"
```

## Error Handling

All casts can raise `InvalidCastConfiguration` when they fail to cast a value. When using fields with `strict_cast=True` in the configuration Meta class, failed casts will raise `CastValueFailure`.

Example:
```python
class AppConfig(Configuration):
    class Meta:
        strict_cast = True  # Will raise errors on cast failures

    port = FieldInt(default="invalid")  # Will raise CastValueFailure
```
