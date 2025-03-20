# Type Casting in Superconf

This tutorial explains how Superconf handles type casting and validation, allowing you to convert configuration values to appropriate types and validate user input.

## Understanding Casts

Casts in Superconf are special classes that convert values from one type to another. They ensure that configuration values have the correct types, regardless of where they come from (environment variables, command line, configuration files, etc.).

The `casts.py` module provides several built-in cast implementations:

- `AsBoolean`: Convert values to boolean
- `AsString`: Convert values to string
- `AsInt`: Convert values to integer
- `AsFloat`: Convert values to float
- `AsList`: Convert values to list
- `AsTuple`: Convert values to tuple
- `AsDict`: Convert values to dictionary
- `AsOption`: Select from predefined options
- `AsIdentity`: Pass values through without conversion
- `AsBest`: Attempt to determine the most appropriate type

## Built-in Casts

Let's look at how to use the built-in casts:

```python
from superconf.casts import (
    as_boolean, as_int, as_string, as_list, 
    as_dict, as_tuple, as_is, as_option, 
    AsOption
)

# Boolean casting
print(as_boolean("yes"))       # True
print(as_boolean("no"))        # False
print(as_boolean("true"))      # True
print(as_boolean("false"))     # False
print(as_boolean("1"))         # True
print(as_boolean("0"))         # False

# Integer casting
print(as_int("42"))            # 42
print(as_int(42.0))            # 42

# String casting
print(as_string(42))           # "42"
print(as_string(True))         # "True"

# List casting
print(as_list("a,b,c"))        # ["a", "b", "c"]
print(as_list(["a", "b"]))     # ["a", "b"]
print(as_list(""))             # []

# Tuple casting
print(as_tuple("a,b,c"))       # ("a", "b", "c")

# Dictionary casting
print(as_dict({"a": 1, "b": 2}))  # {"a": 1, "b": 2}

# Option casting
options = {"dev": "development", "prod": "production"}
option_cast = AsOption(options, default_option="dev")
print(option_cast("prod"))     # "production"
print(option_cast("invalid"))  # "development" (default)
```

## Field Type and Cast Relationship

Each field type in Superconf is associated with a default cast:

- `FieldString` uses `str`
- `FieldInt` uses `as_int`
- `FieldFloat` uses `float`
- `FieldBool` uses `as_boolean`
- `FieldList` uses `as_list`
- `FieldDict` uses `as_dict`
- `FieldTuple` uses `as_tuple`
- `FieldOption` uses `as_option`

When you create a field, it automatically uses the appropriate cast:

```python
from superconf.fields import (
    FieldString, FieldInt, FieldBool, FieldList, 
    FieldDict, FieldOption
)
from superconf.configuration import ContainerConf

class AppConfig(ContainerConf):
    name = FieldString()
    port = FieldInt()
    debug = FieldBool()
    hosts = FieldList()
    env = FieldOption(
        options={"dev": "development", "prod": "production"},
        default_option="dev"
    )

# Values are automatically cast to the right type
config = AppConfig(
    name=42,             # Will be cast to "42"
    port="8000",         # Will be cast to 8000
    debug="yes",         # Will be cast to True
    hosts="host1,host2", # Will be cast to ["host1", "host2"]
    env="prod"           # Will be cast to "production"
)

print(type(config.name))   # <class 'str'>
print(type(config.port))   # <class 'int'>
print(type(config.debug))  # <class 'bool'>
print(type(config.hosts))  # <class 'list'>
```

## Custom Casts

You can create custom casts by subclassing `AbstractCast` and implementing the `__call__` method:

```python
from superconf.casts import AbstractCast
from superconf.exceptions import InvalidCastConfiguration
from superconf.fields import FieldLeaf
from superconf.configuration import ContainerConf

# Custom cast for email validation
class AsEmail(AbstractCast):
    def __call__(self, value):
        value = str(value)
        if "@" not in value or "." not in value:
            raise InvalidCastConfiguration(f"Invalid email format: {value}")
        return value

# Custom cast for URL normalization
class AsUrl(AbstractCast):
    def __call__(self, value):
        value = str(value)
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value

# Custom field using a custom cast
class FieldEmail(FieldLeaf):
    cast = AsEmail()

class FieldUrl(FieldLeaf):
    cast = AsUrl()

# Using custom fields in a configuration
class UserConfig(ContainerConf):
    email = FieldEmail(help="User email address")
    website = FieldUrl(help="User website")

# Create a configuration with custom fields
user = UserConfig(
    email="user@example.com",
    website="example.com"  # Will be normalized to "https://example.com"
)

print(user.email)    # user@example.com
print(user.website)  # https://example.com

# This will raise an error due to invalid email format
try:
    user = UserConfig(email="invalid-email")
except InvalidCastConfiguration as e:
    print(f"Error: {e}")
```

## Implementing Complex Validation

You can implement more complex validation by combining casts with custom field types:

```python
from superconf.casts import AbstractCast, as_int
from superconf.exceptions import InvalidCastConfiguration
from superconf.fields import FieldLeaf
from superconf.configuration import ContainerConf

# Cast for port validation
class AsPort(AbstractCast):
    def __call__(self, value):
        try:
            port = as_int(value)
            if port < 1 or port > 65535:
                raise InvalidCastConfiguration(
                    f"Port must be between 1 and 65535, got: {port}"
                )
            return port
        except (ValueError, TypeError) as e:
            raise InvalidCastConfiguration(f"Invalid port number: {value}") from e

# Cast for version validation (semantic versioning)
class AsSemVer(AbstractCast):
    def __call__(self, value):
        value = str(value)
        parts = value.split(".")
        if len(parts) < 2 or len(parts) > 3:
            raise InvalidCastConfiguration(
                f"Version must be in format 'major.minor[.patch]', got: {value}"
            )
        
        try:
            # Ensure all parts are integers
            for part in parts:
                int(part)
            return value
        except ValueError:
            raise InvalidCastConfiguration(
                f"Version parts must be integers, got: {value}"
            )

# Custom fields using the validation casts
class FieldPort(FieldLeaf):
    cast = AsPort()

class FieldSemVer(FieldLeaf):
    cast = AsSemVer()

# Using custom validation fields
class ServerConfig(ContainerConf):
    hostname = FieldString(default="localhost")
    port = FieldPort(default=8000)
    version = FieldSemVer(default="1.0.0")

# Valid configuration
server = ServerConfig(
    hostname="api.example.com",
    port=5000,
    version="2.1.3"
)

# These will raise validation errors
try:
    invalid_port = ServerConfig(port=70000)  # Port out of range
except InvalidCastConfiguration as e:
    print(f"Port error: {e}")

try:
    invalid_version = ServerConfig(version="1.0.0.0")  # Invalid format
except InvalidCastConfiguration as e:
    print(f"Version error: {e}")
```

## The AsOption Cast

The `AsOption` cast is particularly useful for limiting values to a predefined set:

```python
from superconf.casts import AsOption, FAIL
from superconf.fields import FieldLeaf
from superconf.configuration import ContainerConf

# Create a field with options
class EnvironmentField(FieldLeaf):
    cast = AsOption({
        "dev": "development",
        "test": "testing",
        "staging": "staging",
        "prod": "production"
    })

# With a default option
class LogLevelField(FieldLeaf):
    cast = AsOption({
        "debug": "DEBUG",
        "info": "INFO",
        "warning": "WARNING",
        "error": "ERROR",
        "critical": "CRITICAL"
    }, default_option="info")

# Using option fields
class AppConfig(ContainerConf):
    environment = EnvironmentField(help="Application environment")
    log_level = LogLevelField(help="Logging level")

# Valid values
config = AppConfig(
    environment="prod",
    log_level="debug"
)

print(config.environment)  # "production"
print(config.log_level)    # "DEBUG"

# Invalid environment with no default (will raise error)
try:
    config = AppConfig(environment="invalid")
except Exception as e:
    print(f"Environment error: {e}")

# Invalid log level with default (will use default)
config = AppConfig(log_level="trace")
print(config.log_level)    # "INFO" (default)
```

## Working with List and Dict Casts

Superconf has special handling for list and dictionary casting:

```python
from superconf.casts import AsList, AsDict
from superconf.fields import FieldList, FieldDict
from superconf.configuration import ContainerConf

# Custom list cast with different delimiter
class CommaSeparatedList(AsList):
    def __init__(self):
        super().__init__(delimiter=",")

# Custom dictionary cast
class KeyValueDict(AsDict):
    def __init__(self):
        super().__init__()
    
    # Custom parsing for "key=value" format
    def _parse(self, value):
        if isinstance(value, str):
            result = {}
            pairs = value.split(";")
            for pair in pairs:
                if "=" in pair:
                    key, val = pair.split("=", 1)
                    result[key.strip()] = val.strip()
            return result
        return super()._parse(value)

# Custom fields with specialized casts
class FieldCSV(FieldList):
    cast = CommaSeparatedList()

class FieldKeyValue(FieldDict):
    cast = KeyValueDict()

# Using custom collection fields
class ApiConfig(ContainerConf):
    tags = FieldCSV(default="api,v1")
    headers = FieldKeyValue(help="HTTP headers")

# Create configuration instance
api = ApiConfig(
    tags="auth,users,v2",
    headers="Content-Type=application/json; Accept=application/json"
)

print(api.tags)      # ["auth", "users", "v2"]
print(api.headers)   # {"Content-Type": "application/json", "Accept": "application/json"}
```

## Combining Casts

You can combine multiple casts to create more complex validation chains:

```python
from superconf.casts import AbstractCast, as_list, as_int
from superconf.exceptions import InvalidCastConfiguration
from superconf.fields import FieldLeaf
from superconf.configuration import ContainerConf

# Cast for a list of integers
class AsIntList(AbstractCast):
    def __call__(self, value):
        # First convert to list
        items = as_list(value)
        # Then convert each item to int
        result = []
        for item in items:
            try:
                result.append(as_int(item))
            except Exception as e:
                raise InvalidCastConfiguration(f"Could not convert {item} to int") from e
        return result

# Cast for a range of values
class AsRange(AbstractCast):
    def __init__(self, min_val=None, max_val=None):
        self.min_val = min_val
        self.max_val = max_val
    
    def __call__(self, value):
        value = as_int(value)
        if self.min_val is not None and value < self.min_val:
            raise InvalidCastConfiguration(f"Value {value} is less than minimum {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise InvalidCastConfiguration(f"Value {value} is greater than maximum {self.max_val}")
        return value

# Custom fields using combined casts
class FieldIntList(FieldLeaf):
    cast = AsIntList()

class FieldPort(FieldLeaf):
    cast = AsRange(min_val=1, max_val=65535)

# Using combined cast fields
class NetworkConfig(ContainerConf):
    ports = FieldIntList(default="80,443")
    threads = FieldPort(default=8)

# Create configuration
net = NetworkConfig(
    ports="8080,9000,3000",
    threads=16
)

print(net.ports)     # [8080, 9000, 3000]
print(net.threads)   # 16

# These will raise validation errors
try:
    invalid = NetworkConfig(ports="80,invalid,443")
except InvalidCastConfiguration as e:
    print(f"Ports error: {e}")

try:
    invalid = NetworkConfig(threads=70000)
except InvalidCastConfiguration as e:
    print(f"Threads error: {e}")
```

## Next Steps

Now that you understand type casting in Superconf, you can:

- Implement custom casts for your specific validation needs
- Create specialized field types for common patterns
- Combine casts for complex validation chains
- Explore how to integrate validation with configuration loading 