# Configuration Basics

This tutorial covers the fundamentals of creating and working with configuration classes in Superconf.

## Configuration Classes

In Superconf, configuration is defined using classes that inherit from `ContainerConf`. Each attribute of the class represents a configuration field with its type, default value, and other metadata.

```python
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost", help="Database host")
    port = FieldInt(default=5432, help="Database port")
    user = FieldString(help="Database user")
    password = FieldString(help="Database password")
    use_ssl = FieldBool(default=False, help="Use SSL for connection")
```

## Field Types

Superconf provides different field types to handle various data types:

- `FieldString`: For text values
- `FieldInt`: For integer values 
- `FieldFloat`: For floating-point values
- `FieldBool`: For boolean values
- `FieldList`: For list values
- `FieldDict`: For dictionary values
- `FieldTuple`: For tuple values
- `FieldOption`: For values that must be one of a predefined set
- `FieldConf`: For nested configuration objects

Let's create a more complex configuration with different field types:

```python
from superconf.fields import (
    FieldString, FieldInt, FieldBool, FieldList, 
    FieldDict, FieldOption, FieldConf
)
from superconf.configuration import ContainerConf

class LogConfig(ContainerConf):
    level = FieldOption(
        options={
            "debug": "DEBUG",
            "info": "INFO", 
            "warning": "WARNING",
            "error": "ERROR",
            "critical": "CRITICAL"
        },
        default_option="info",
        help="Logging level"
    )
    file = FieldString(default="app.log", help="Log file path")
    format = FieldString(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp", help="Application name")
    version = FieldString(default="1.0.0", help="Application version")
    debug = FieldBool(default=False, help="Enable debug mode")
    
    # List of allowed origins for CORS
    allowed_origins = FieldList(default=["http://localhost:3000"], help="CORS allowed origins")
    
    # Database configuration as a nested config
    database = FieldConf(
        LogConfig,
        help="Database configuration"
    )
    
    # Feature flags dictionary
    features = FieldDict(default={"dark_mode": True, "analytics": False}, help="Feature flags")
```

## Working with Configuration Instances

Once you've defined a configuration class, you can create instances and work with them:

```python
# Create a configuration instance with default values
config = AppConfig()

# Access configuration values
print(f"App name: {config.name}")
print(f"Debug mode: {config.debug}")
print(f"Allowed origins: {config.allowed_origins}")

# Override values during initialization
config_dev = AppConfig(
    name="MyApp-Dev",
    debug=True,
    database={"host": "dev-db", "port": 5433}
)

# Update values after initialization
config_dev.features["experimental"] = True

# Access nested configuration
print(f"Database host: {config_dev.database.host}")
print(f"Log level: {config_dev.log.level}")  # Will return "INFO" from the default_option
```

## Default Values and Required Fields

Fields can have default values or be required:

- If a field has a default value, it will be used when no value is provided
- If a field doesn't have a default value, it's considered required and must be provided when creating a configuration instance

```python
class UserConfig(ContainerConf):
    username = FieldString(help="Required username")  # Required (no default)
    email = FieldString(help="Required email")  # Required (no default)
    notifications = FieldBool(default=True, help="Enable notifications")  # Optional with default
```

When creating an instance of a configuration with required fields, you must provide values for those fields:

```python
# This will raise an exception because username and email are required
try:
    user_config = UserConfig()
except Exception as e:
    print(f"Error: {e}")

# This is correct - providing values for required fields
user_config = UserConfig(username="john_doe", email="john@example.com")
```

## Validation and Type Casting

Superconf automatically validates and casts values to the correct type:

```python
# The port value "8000" will be cast to an integer
config = AppConfig(port="8000")
print(type(config.port))  # <class 'int'>

# Boolean fields accept various string representations
config = AppConfig(debug="yes")  # Will be cast to True
print(config.debug)  # True

# List fields accept comma-separated strings
config = AppConfig(allowed_origins="http://localhost:3000,http://example.com")
print(config.allowed_origins)  # ['http://localhost:3000', 'http://example.com']
```

## Next Steps

Now that you understand the basics of configuration in Superconf, you can move on to more advanced topics:

- Hierarchical configuration and inheritance
- Loading configuration from files
- Path handling with PathAnchor
- Custom field types and validation 