# How to Create Custom Field Types

<div align="center">
  <p><em>Learn how to create specialized field types with validation and transformation in Superconf</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">⚡ How-To Guides</a> |
  <a href="02_environment_variables.md">⏮️ Previous: Environment Variables</a> |
  <a href="04_config_inheritance.md">⏭️ Next: Configuration Inheritance</a>
</p>

---

This guide explains how to create custom field types in Superconf for specialized configuration needs.

## Understanding Field Types

Superconf field types manage type conversion and validation for configuration values. Each field type is associated with a cast function that converts input values to the appropriate type.

The built-in field types include:
- `FieldString`: For string values
- `FieldInt`: For integer values
- `FieldBool`: For boolean values
- `FieldList`: For list values
- `FieldDict`: For dictionary values
- `FieldTuple`: For tuple values
- `FieldOption`: For values selected from predefined options
- `FieldConf`: For nested configuration classes

## Basic Custom Field Types

Let's create some basic custom field types:

```python
from superconf.fields import FieldLeaf
from superconf.casts import AbstractCast
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf
import re

# Custom cast for email validation
class AsEmail(AbstractCast):
    def __call__(self, value):
        value = str(value)
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise InvalidCastConfiguration(f"Invalid email format: {value}")
        return value

# Custom cast for URL normalization
class AsUrl(AbstractCast):
    def __call__(self, value):
        value = str(value)
        if not value.startswith(("http://", "https://")):
            value = "https://" + value
        return value

# Custom field types using the custom casts
class FieldEmail(FieldLeaf):
    cast = AsEmail()

class FieldUrl(FieldLeaf):
    cast = AsUrl()

# Using the custom fields
class UserConfig(ContainerConf):
    name = FieldString(default="User")
    email = FieldEmail(help="User email address")
    website = FieldUrl(help="User website")

# Creating a configuration instance
user = UserConfig(
    name="John Doe",
    email="john@example.com",
    website="example.com"  # Will be normalized to "https://example.com"
)

print(user.name)     # "John Doe"
print(user.email)    # "john@example.com"
print(user.website)  # "https://example.com"

# This will raise an error due to invalid email format
try:
    invalid_user = UserConfig(email="invalid-email")
except InvalidCastConfiguration as e:
    print(f"Error: {e}")
```

## Fields with Validation

You can create fields with complex validation rules:

```python
from superconf.fields import FieldLeaf
from superconf.casts import AbstractCast, as_int
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf

# Cast with validation for port numbers
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

# Cast with validation for version strings
class AsSemVer(AbstractCast):
    def __call__(self, value):
        value = str(value)
        parts = value.split(".")
        
        # Check format (major.minor.patch)
        if len(parts) < 2 or len(parts) > 3:
            raise InvalidCastConfiguration(
                f"Version must be in format 'major.minor[.patch]', got: {value}"
            )
        
        # Validate that each part is a number
        try:
            for part in parts:
                int(part)
            return value
        except ValueError:
            raise InvalidCastConfiguration(
                f"Version parts must be integers, got: {value}"
            )

# Custom field types with validation
class FieldPort(FieldLeaf):
    cast = AsPort()

class FieldSemVer(FieldLeaf):
    cast = AsSemVer()

# Using the custom validation fields
class ServerConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldPort(default=8000)
    version = FieldSemVer(default="1.0.0")

# Valid configuration
server = ServerConfig(
    host="api.example.com",
    port=5000,
    version="2.1.3"
)

print(f"Server: {server.host}:{server.port} (v{server.version})")

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

## Fields with Transformation

You can create fields that transform input values:

```python
from superconf.fields import FieldLeaf
from superconf.casts import AbstractCast
from superconf.configuration import ContainerConf

# Cast that converts path separators
class AsPath(AbstractCast):
    def __call__(self, value):
        # Normalize path separators based on OS
        import os
        return str(value).replace('\\', '/').replace('//', '/')

# Cast that transforms case
class AsUpperCase(AbstractCast):
    def __call__(self, value):
        return str(value).upper()

class AsLowerCase(AbstractCast):
    def __call__(self, value):
        return str(value).lower()

# Cast that truncates strings
class AsTruncated(AbstractCast):
    def __init__(self, max_length=10, suffix="..."):
        self.max_length = max_length
        self.suffix = suffix
        
    def __call__(self, value):
        value = str(value)
        if len(value) <= self.max_length:
            return value
        return value[:self.max_length] + self.suffix

# Custom field types with transformations
class FieldPath(FieldLeaf):
    cast = AsPath()

class FieldUpperCase(FieldLeaf):
    cast = AsUpperCase()

class FieldLowerCase(FieldLeaf):
    cast = AsLowerCase()

class FieldTruncated(FieldLeaf):
    cast = AsTruncated(max_length=15)

# Using transform fields
class FormatConfig(ContainerConf):
    path = FieldPath()
    upper = FieldUpperCase()
    lower = FieldLowerCase()
    summary = FieldTruncated()

# Create configuration with transformations
format_config = FormatConfig(
    path="C:\\Users\\user\\Documents//file.txt",
    upper="convert to uppercase",
    lower="CONVERT TO LOWERCASE",
    summary="This is a very long description that will be truncated"
)

print(format_config.path)     # "C:/Users/user/Documents/file.txt"
print(format_config.upper)    # "CONVERT TO UPPERCASE"
print(format_config.lower)    # "convert to lowercase"
print(format_config.summary)  # "This is a very ..."
```

## Fields with Custom Constructors

You can create fields that require additional parameters:

```python
from superconf.fields import FieldLeaf
from superconf.casts import AbstractCast, FAIL
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf

# Cast with configurable validation
class AsStringWithConstraints(AbstractCast):
    def __init__(self, 
                 min_length=None, 
                 max_length=None,
                 regex=None,
                 allowed_values=None):
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex
        self.allowed_values = allowed_values
        
    def __call__(self, value):
        value = str(value)
        
        # Check minimum length
        if self.min_length is not None and len(value) < self.min_length:
            raise InvalidCastConfiguration(
                f"Value '{value}' is too short (min: {self.min_length})"
            )
        
        # Check maximum length
        if self.max_length is not None and len(value) > self.max_length:
            raise InvalidCastConfiguration(
                f"Value '{value}' is too long (max: {self.max_length})"
            )
        
        # Check regex pattern
        if self.regex is not None:
            import re
            if not re.match(self.regex, value):
                raise InvalidCastConfiguration(
                    f"Value '{value}' does not match pattern: {self.regex}"
                )
        
        # Check allowed values
        if self.allowed_values is not None:
            if value not in self.allowed_values:
                raise InvalidCastConfiguration(
                    f"Value '{value}' not in allowed values: {self.allowed_values}"
                )
                
        return value

# Custom fields with parameters
class FieldUsername(FieldLeaf):
    def __init__(self, **kwargs):
        # Define validation constraints
        self.cast = AsStringWithConstraints(
            min_length=3,
            max_length=20,
            regex=r'^[a-zA-Z0-9_]+$'
        )
        super().__init__(**kwargs)

class FieldCountryCode(FieldLeaf):
    def __init__(self, **kwargs):
        # Define allowed values
        self.cast = AsStringWithConstraints(
            allowed_values=["US", "CA", "UK", "FR", "DE", "JP", "AU"]
        )
        super().__init__(**kwargs)

# Use fields with custom constraints
class UserProfile(ContainerConf):
    username = FieldUsername(help="Username (3-20 chars, alphanumeric + underscore)")
    country = FieldCountryCode(default="US", help="Country code")

# Valid configuration
user = UserProfile(username="john_doe", country="UK")
print(f"User: {user.username} from {user.country}")

# These will raise validation errors
try:
    invalid_user = UserProfile(username="a")  # Too short
except InvalidCastConfiguration as e:
    print(f"Username error: {e}")

try:
    invalid_user = UserProfile(username="john.doe")  # Invalid character
except InvalidCastConfiguration as e:
    print(f"Username error: {e}")

try:
    invalid_user = UserProfile(country="Brazil")  # Not in allowed values
except InvalidCastConfiguration as e:
    print(f"Country error: {e}")
```

## Field Subclasses

You can create field subclasses with built-in functionality:

```python
from superconf.fields import FieldString, FieldInt, FieldList
from superconf.casts import AbstractCast, as_list, as_int
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf
import os

# Cast for file path validation
class AsFilePath(AbstractCast):
    def __init__(self, must_exist=False, must_be_file=False, must_be_dir=False):
        self.must_exist = must_exist
        self.must_be_file = must_be_file
        self.must_be_dir = must_be_dir
    
    def __call__(self, value):
        path = str(value)
        
        if self.must_exist and not os.path.exists(path):
            raise InvalidCastConfiguration(f"Path does not exist: {path}")
            
        if self.must_be_file and not os.path.isfile(path):
            raise InvalidCastConfiguration(f"Path is not a file: {path}")
            
        if self.must_be_dir and not os.path.isdir(path):
            raise InvalidCastConfiguration(f"Path is not a directory: {path}")
            
        return path

# Cast for integer ranges
class AsIntRange(AbstractCast):
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
    
    def __call__(self, value):
        value = as_int(value)
        
        if self.min_value is not None and value < self.min_value:
            raise InvalidCastConfiguration(
                f"Value {value} is less than minimum {self.min_value}"
            )
            
        if self.max_value is not None and value > self.max_value:
            raise InvalidCastConfiguration(
                f"Value {value} is greater than maximum {self.max_value}"
            )
            
        return value

# Cast for processing lists of integers
class AsIntList(AbstractCast):
    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value
    
    def __call__(self, value):
        items = as_list(value)
        result = []
        
        for item in items:
            try:
                int_value = as_int(item)
                
                # Apply range validation if specified
                if self.min_value is not None and int_value < self.min_value:
                    raise InvalidCastConfiguration(
                        f"Value {int_value} is less than minimum {self.min_value}"
                    )
                
                if self.max_value is not None and int_value > self.max_value:
                    raise InvalidCastConfiguration(
                        f"Value {int_value} is greater than maximum {self.max_value}"
                    )
                
                result.append(int_value)
            except Exception as e:
                raise InvalidCastConfiguration(f"Invalid integer: {item}") from e
                
        return result

# Field subclasses
class FieldFilePath(FieldString):
    def __init__(self, must_exist=False, must_be_file=False, must_be_dir=False, **kwargs):
        self.cast = AsFilePath(
            must_exist=must_exist,
            must_be_file=must_be_file,
            must_be_dir=must_be_dir
        )
        super().__init__(**kwargs)

class FieldIntRange(FieldInt):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.cast = AsIntRange(min_value=min_value, max_value=max_value)
        super().__init__(**kwargs)

class FieldIntList(FieldList):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.cast = AsIntList(min_value=min_value, max_value=max_value)
        super().__init__(**kwargs)

# Using field subclasses
class AppConfig(ContainerConf):
    config_file = FieldFilePath(
        default="config.yml",
        must_exist=True,
        must_be_file=True,
        help="Configuration file (must exist)"
    )
    
    log_dir = FieldFilePath(
        default="logs",
        must_be_dir=True,
        help="Log directory (must be a directory)"
    )
    
    port = FieldIntRange(
        default=8000,
        min_value=1024,
        max_value=65535,
        help="Port number (1024-65535)"
    )
    
    worker_counts = FieldIntList(
        default="2,4,8",
        min_value=1,
        max_value=32,
        help="Worker counts (comma-separated, 1-32)"
    )

# Using the custom fields
# Note: This example assumes config.yml exists and logs directory exists
try:
    config = AppConfig()
    
    print(f"Config file: {config.config_file}")
    print(f"Log directory: {config.log_dir}")
    print(f"Port: {config.port}")
    print(f"Worker counts: {config.worker_counts}")
    
except InvalidCastConfiguration as e:
    print(f"Configuration error: {e}")
```

## Fields for Special Data Types

You can create fields for specialized data types:

```python
from superconf.fields import FieldLeaf
from superconf.casts import AbstractCast
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf
from datetime import datetime, date, time
import json
import base64
import uuid

# Cast for datetime objects
class AsDateTime(AbstractCast):
    def __init__(self, format="%Y-%m-%d %H:%M:%S"):
        self.format = format
    
    def __call__(self, value):
        if isinstance(value, datetime):
            return value
            
        try:
            if isinstance(value, str):
                return datetime.strptime(value, self.format)
            elif isinstance(value, (int, float)):
                return datetime.fromtimestamp(value)
        except Exception as e:
            raise InvalidCastConfiguration(f"Invalid datetime: {value}") from e

# Cast for date objects
class AsDate(AbstractCast):
    def __init__(self, format="%Y-%m-%d"):
        self.format = format
    
    def __call__(self, value):
        if isinstance(value, date):
            return value
            
        try:
            if isinstance(value, str):
                return datetime.strptime(value, self.format).date()
            elif isinstance(value, (int, float)):
                return datetime.fromtimestamp(value).date()
        except Exception as e:
            raise InvalidCastConfiguration(f"Invalid date: {value}") from e

# Cast for JSON
class AsJson(AbstractCast):
    def __call__(self, value):
        if isinstance(value, (dict, list)):
            return value
            
        try:
            if isinstance(value, str):
                return json.loads(value)
        except Exception as e:
            raise InvalidCastConfiguration(f"Invalid JSON: {value}") from e

# Cast for UUID
class AsUuid(AbstractCast):
    def __call__(self, value):
        if isinstance(value, uuid.UUID):
            return value
            
        try:
            return uuid.UUID(str(value))
        except Exception as e:
            raise InvalidCastConfiguration(f"Invalid UUID: {value}") from e

# Cast for base64
class AsBase64(AbstractCast):
    def __call__(self, value):
        if isinstance(value, bytes):
            return base64.b64encode(value).decode('utf-8')
        elif isinstance(value, str):
            # Check if already base64
            try:
                base64.b64decode(value)
                return value
            except Exception:
                # Not base64, encode it
                return base64.b64encode(value.encode('utf-8')).decode('utf-8')
        else:
            raise InvalidCastConfiguration(f"Cannot convert to base64: {value}")

# Custom field types
class FieldDateTime(FieldLeaf):
    def __init__(self, format="%Y-%m-%d %H:%M:%S", **kwargs):
        self.cast = AsDateTime(format=format)
        super().__init__(**kwargs)

class FieldDate(FieldLeaf):
    def __init__(self, format="%Y-%m-%d", **kwargs):
        self.cast = AsDate(format=format)
        super().__init__(**kwargs)

class FieldJson(FieldLeaf):
    cast = AsJson()

class FieldUuid(FieldLeaf):
    cast = AsUuid()

class FieldBase64(FieldLeaf):
    cast = AsBase64()

# Using special data type fields
class EventConfig(ContainerConf):
    id = FieldUuid(help="Event ID")
    timestamp = FieldDateTime(help="Event timestamp")
    date = FieldDate(help="Event date")
    metadata = FieldJson(default="{}", help="Event metadata (JSON)")
    secret = FieldBase64(help="Base64-encoded secret")

# Create configuration with special types
event = EventConfig(
    id="550e8400-e29b-41d4-a716-446655440000",
    timestamp="2023-04-01 14:30:00",
    date="2023-04-01",
    metadata='{"type": "user_login", "source": "web"}',
    secret="my_secret_value"
)

print(f"Event ID: {event.id}, type: {type(event.id)}")  # UUID object
print(f"Timestamp: {event.timestamp}, type: {type(event.timestamp)}")  # datetime object
print(f"Date: {event.date}, type: {type(event.date)}")  # date object
print(f"Metadata: {event.metadata}, type: {type(event.metadata)}")  # dict
print(f"Secret: {event.secret}")  # base64 encoded string
```

## Custom Collection Fields

You can create custom collection fields:

```python
from superconf.fields import FieldLeaf, FieldList, FieldDict
from superconf.casts import AbstractCast, AsList, AsDict
from superconf.exceptions import InvalidCastConfiguration
from superconf.configuration import ContainerConf

# Custom list casts
class AsCSV(AsList):
    """Cast for comma-separated values with custom processing"""
    def __init__(self, strip=True, unique=False, sort=False):
        super().__init__(delimiter=",")
        self.strip = strip
        self.unique = unique
        self.sort = sort
    
    def __call__(self, value):
        items = super().__call__(value)
        
        if self.strip:
            items = [item.strip() if isinstance(item, str) else item for item in items]
            
        if self.unique:
            items = list(dict.fromkeys(items))  # Preserves order
            
        if self.sort:
            items = sorted(items)
            
        return items

# Custom dict casts
class AsKeyValuePairs(AsDict):
    """Cast for key=value formatted strings"""
    def __init__(self, item_separator=",", key_value_separator="="):
        super().__init__()
        self.item_separator = item_separator
        self.key_value_separator = key_value_separator
    
    def __call__(self, value):
        if isinstance(value, str):
            result = {}
            pairs = value.split(self.item_separator)
            
            for pair in pairs:
                if self.key_value_separator in pair:
                    key, val = pair.split(self.key_value_separator, 1)
                    result[key.strip()] = val.strip()
            
            return result
            
        return super().__call__(value)

# Custom field types
class FieldCSV(FieldList):
    def __init__(self, strip=True, unique=False, sort=False, **kwargs):
        self.cast = AsCSV(strip=strip, unique=unique, sort=sort)
        super().__init__(**kwargs)

class FieldKeyValuePairs(FieldDict):
    def __init__(self, item_separator=",", key_value_separator="=", **kwargs):
        self.cast = AsKeyValuePairs(
            item_separator=item_separator,
            key_value_separator=key_value_separator
        )
        super().__init__(**kwargs)

# Using custom collection fields
class ApiConfig(ContainerConf):
    tags = FieldCSV(
        default="api,rest,v1",
        unique=True,
        sort=True,
        help="API tags (unique, sorted)"
    )
    
    cors_origins = FieldCSV(
        default="localhost,example.com",
        help="CORS allowed origins"
    )
    
    headers = FieldKeyValuePairs(
        default="Content-Type=application/json, Accept=application/json",
        help="HTTP headers (key=value pairs)"
    )
    
    query_params = FieldKeyValuePairs(
        item_separator="&",
        key_value_separator="=",
        default="page=1&limit=100",
        help="Query parameters (key=value pairs with & separator)"
    )

# Create configuration with custom collections
api = ApiConfig(
    tags="api, rest, v1, graphql, rest",  # Duplicates will be removed
    cors_origins="localhost, example.com, test.com",
    headers="Content-Type=application/json, Authorization=Bearer token",
    query_params="page=1&limit=50&sort=created_at"
)

print(f"Tags: {api.tags}")  # ['api', 'graphql', 'rest', 'v1']
print(f"CORS Origins: {api.cors_origins}")  # ['localhost', 'example.com', 'test.com']
print(f"Headers: {api.headers}")  # {'Content-Type': 'application/json', 'Authorization': 'Bearer token'}
print(f"Query Params: {api.query_params}")  # {'page': '1', 'limit': '50', 'sort': 'created_at'}
```

## Best Practices for Custom Fields

When creating custom field types in Superconf:

1. **Extend from the appropriate base class**:
   - Use `FieldLeaf` for simple value fields
   - Use `FieldList`, `FieldDict`, etc. for collection fields
   - Use inheritance to build on existing fields

2. **Create robust casts**:
   - Implement proper error handling with clear error messages
   - Handle various input types (strings, numbers, etc.)
   - Return values consistently

3. **Document your fields**:
   - Add docstrings to explain field behavior
   - Document parameters and validation rules
   - Include examples in comments

4. **Design for reusability**:
   - Make fields configurable with parameters
   - Avoid hardcoding values that might change
   - Create fields that can be composed with other fields

5. **Balance validation with flexibility**:
   - Validate inputs to ensure correctness
   - Provide helpful error messages
   - Convert input formats when reasonable

## Summary

Custom field types in Superconf allow you to:
- Validate configuration values with specific rules
- Transform input values into appropriate formats
- Support specialized data types
- Create reusable configuration components

By creating custom field types, you can make your configuration more robust, more type-safe, and more self-documenting. 