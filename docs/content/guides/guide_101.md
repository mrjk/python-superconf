# SuperConf User Guide

This guide will walk you through the basic usage of SuperConf, a powerful configuration management library for Python.

## Basic Usage

### 1. Creating a Configuration Class

The most basic way to use SuperConf is to create a configuration class that inherits from `Configuration`:

```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldBool

class AppConfig(Configuration):
    # Define your configuration fields
    debug = FieldBool(default=False, help="Enable debug mode")
    port = FieldInt(default=8080, help="Server port")
    app_name = FieldString(default="myapp", help="Application name")
    api_key = FieldString(help="API key for external service")  # No default value

# Create an instance
config = AppConfig()

# Access configuration values
print(config.debug)    # False (default value)
print(config.port)     # 8080 (default value)
print(config.api_key)  # None (no default value was set)

# Check if a field has a value set
print(config.is_set('debug'))     # True (has default value)
print(config.is_set('api_key'))   # False (no value set)
```

### 2. Loading Configuration Values

You can provide values when creating a configuration instance:

```python
config = AppConfig(values={
    'debug': True,
    'port': 9000,
    'app_name': 'production-app',
    'api_key': 'secret-key'
})

print(config.debug)     # True
print(config.port)      # 9000
print(config.app_name)  # "production-app"
print(config.api_key)   # "secret-key"
```

### 3. Environment Variables

SuperConf follows the [12-factor app methodology](https://12factor.net/config) for configuration management. It automatically maps class attributes to environment variables using uppercase:

```bash
# Set environment variables
export APP_DEBUG=true
export APP_PORT=9000
export APP_NAME="production-app"

# Python code
config = AppConfig()
print(config.debug)    # True
print(config.port)     # 9000
print(config.app_name) # "production-app"
```

### 4. Working with Lists and Dictionaries

For more complex data types:

```python
from superconf.fields import FieldList, FieldDict

class AdvancedConfig(Configuration):
    plugins = FieldList(default=["core"], help="Enabled plugins")
    database = FieldDict(default={
        "host": "localhost",
        "port": 5432
    }, help="Database configuration")

# Set via environment variables
export APP_PLUGINS="core,auth,cache"
# For dictionaries (future implementation):
export APP_DATABASE_HOST="db.example.com"
export APP_DATABASE_PORT="5432"
export APP_DATABASE_USER="admin"

config = AdvancedConfig()
print(config.plugins)  # ["core", "auth", "cache"]
# Note: Dictionary environment variables support is planned for future releases
```

While dictionaries are useful for simple key-value configurations, for more complex nested structures, please refer to our [Nested Configuration Guide](guide_102_nested.md).

