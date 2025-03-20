# Configuration Loading

<div align="center">
  <p><em>Understanding the design and internal workings of Superconf's configuration loading system</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">🔍 Implementation</a> |
  <a href="04_validation_architecture.md">⏮️ Previous: Validation Architecture</a>
</p>

---

This document explains the design and internal workings of Superconf's configuration loading system.

## The Purpose of Configuration Loading

Configuration loading in Superconf serves several important purposes:

1. **Data acquisition** - Reading configuration data from various sources
2. **Data normalization** - Converting data into a consistent internal format
3. **Type conversion** - Ensuring configuration values have the correct types
4. **Default application** - Applying default values where needed
5. **Validation** - Verifying that the loaded configuration is valid
6. **Instantiation** - Creating a configuration object with the loaded data

## Architecture Overview

Superconf's configuration loading architecture is designed around the idea of separation between:

1. **Configuration structure** - Defined by `ContainerConf` classes
2. **Configuration values** - Provided from various sources
3. **Loading mechanisms** - Responsible for bridging the gap between sources and structure

This separation allows for flexibility in how configuration is defined and loaded.

## Configuration Sources

Superconf supports loading configuration from various sources:

1. **Python dictionaries** - Direct in-code configuration
2. **YAML files** - Human-readable configuration files
3. **JSON files** - Machine-friendly configuration files
4. **Environment variables** - System-level configuration
5. **Command-line arguments** - Runtime overrides
6. **Database** - Persistent configuration storage

Each source has its own characteristics and appropriate use cases.

## The Loading Process

The general configuration loading process in Superconf consists of these steps:

1. **Read** data from the source
2. **Parse** the data into a Python dictionary
3. **Apply** the data to a configuration class
4. **Validate** the resulting configuration object

Here's a simplified example:

```python
class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)

# Step 1: Read data from the source
with open("config.yml", "r") as file:
    yaml_data = file.read()

# Step 2: Parse the data into a Python dictionary
import yaml
config_dict = yaml.safe_load(yaml_data)

# Step 3: Apply the data to a configuration class
config = AppConfig(**config_dict)

# Step 4: Validation happens automatically during instantiation
```

## Loading from Files

Superconf provides utilities for loading configuration from files:

```python
import yaml
from superconf.anchors import FileAnchor
from superconf.configuration import ContainerConf

class AppConfig(ContainerConf):
    # Configuration fields defined here...

def load_config(file_path):
    """Load configuration from a YAML file"""
    file_anchor = FileAnchor(file_path)
    path = file_anchor.get_path()
    
    with open(path, "r") as file:
        config_data = yaml.safe_load(file)
    
    return AppConfig(**config_data)
```

For more details on file loading, see [Loading Configuration from Files](../howto/01_loading_from_files.md).

## Loading from Environment Variables

Superconf supports loading configuration from environment variables:

```python
import os
from superconf.configuration import ContainerConf

class AppConfig(ContainerConf):
    # Configuration fields defined here...

def load_from_env(prefix="APP_"):
    """Load configuration from environment variables"""
    config_data = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            config_data[config_key] = value
    
    return AppConfig(**config_data)
```

For more details on environment variable loading, see [Using Environment Variables](../howto/02_environment_variables.md).

## The Role of Cast Functions

Cast functions play a crucial role in configuration loading:

1. They convert values from source formats to the appropriate Python types
2. They validate that values can be properly converted
3. They provide clear error messages when conversion fails

For example, when loading a port number from a configuration file:

```yaml
# config.yml
port: "8080"
```

The `FieldInt` cast function will convert the string `"8080"` to the integer `8080`.

For more details on cast functions, see [Type Casting System](03_type_casting.md).

## Layered Configuration Loading

In real-world applications, configuration is often loaded from multiple sources in layers:

```python
def load_layered_config():
    """Load configuration from multiple sources in order of precedence"""
    # Start with default configuration
    config = AppConfig()
    
    # Layer 1: Load from base configuration file
    try:
        base_config = load_from_file("config.yml")
        config.merge(base_config)
    except FileNotFoundError:
        pass  # Base config is optional
    
    # Layer 2: Load from environment-specific configuration
    env = os.environ.get("APP_ENV", "dev")
    try:
        env_config = load_from_file(f"config.{env}.yml")
        config.merge(env_config)
    except FileNotFoundError:
        pass  # Environment config is optional
    
    # Layer 3: Load from environment variables (highest precedence)
    env_config = load_from_env("APP_")
    config.merge(env_config)
    
    return config
```

This layered approach allows for:
- Default configuration values
- Environment-specific overrides
- Runtime configuration through environment variables

## Merging Configurations

Superconf provides a `merge` method for combining configurations:

```python
# Load configuration from a file
file_config = load_from_file("config.yml")

# Load configuration from environment variables
env_config = load_from_env("APP_")

# Merge configurations (env_config takes precedence)
file_config.merge(env_config)
```

The `merge` method follows these rules:
1. Values from the source configuration override values in the target
2. Only fields that exist in both configurations are merged
3. Nested configurations are merged recursively
4. Container fields (lists, dicts) are replaced, not merged

## Nested Configuration Loading

Superconf supports loading nested configuration structures:

```python
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()
    user = FieldString()
    password = FieldString()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    database = FieldConf(DatabaseConfig)

# Load from a YAML file
"""
# config.yml
name: MyService
database:
  host: db.example.com
  port: 5432
  name: myservice
  user: admin
  password: secret
"""
```

The nested structure in the YAML file matches the nested structure of the configuration classes.

## Partial Configuration Loading

Superconf allows loading partial configurations, where some values are provided and others use defaults:

```python
class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    log_level = FieldString(default="info")

# Load a partial configuration
config = AppConfig(name="MyService", port=9000)

# The remaining fields use defaults
print(config.debug)      # False
print(config.log_level)  # "info"
```

This flexibility allows for concise configuration files that only specify non-default values.

## Error Handling During Loading

Superconf provides clear error messages when configuration loading fails:

```python
try:
    config = AppConfig(port="not_a_number")
except InvalidCastConfiguration as e:
    print(f"Error: {e}")
    # Error: Cannot convert to int: not_a_number (field: port)
```

These error messages help quickly identify and fix configuration issues.

## Configuration Validation During Loading

Validation is automatically performed during configuration loading:

1. **Field-level validation** - Ensuring each field has a valid value
2. **Container-level validation** - Verifying relationships between fields
3. **Custom validation** - Applying application-specific validation rules

For more details on validation, see [Validation Architecture](04_validation_architecture.md).

## Path Anchors for File Loading

Superconf uses path anchors to make file paths more flexible:

```python
from superconf.anchors import PathAnchor, FileAnchor

# Create path anchors
root = PathAnchor(os.path.abspath(os.path.dirname(__file__)))
config_dir = PathAnchor("config", parent=root)

# Create file anchors
config_file = FileAnchor("config.yml", parent=config_dir)
secrets_file = FileAnchor("secrets.yml", parent=config_dir)

# Load configuration from anchored files
config_path = config_file.get_path()
secrets_path = secrets_file.get_path()
```

Path anchors allow for:
- Portable configuration paths across different environments
- Relative paths that work regardless of current working directory
- Clear organization of configuration file locations

## Dynamic Configuration Sources

Superconf can be extended to support dynamic configuration sources:

```python
class DatabaseConfigSource:
    def __init__(self, connection_string):
        self.connection_string = connection_string
    
    def load_config(self, config_class):
        """Load configuration from a database"""
        # Connect to database
        # Query configuration data
        # Convert to dictionary
        # Return instance of config_class
```

This extensibility allows for custom configuration sources tailored to specific application needs.

## Configuration Factories

Superconf works well with factory functions that create pre-configured instances:

```python
def create_app_config(env="dev"):
    """Create a configuration for the specified environment"""
    # Load base configuration
    config = AppConfig()
    
    # Load environment-specific configuration
    if env == "dev":
        config.merge(AppConfig(debug=True, log_level="debug"))
    elif env == "prod":
        config.merge(AppConfig(debug=False, log_level="warning"))
    
    return config
```

These factories can encapsulate complex configuration loading logic.

## Handling Sensitive Data

Superconf supports strategies for handling sensitive data during configuration loading:

```python
def load_secure_config():
    """Load configuration with sensitive data from separate sources"""
    # Load main configuration
    config = load_from_file("config.yml")
    
    # Load sensitive data from environment variables
    if "DB_PASSWORD" in os.environ:
        config.database.password = os.environ["DB_PASSWORD"]
    
    return config
```

This approach allows sensitive data to be stored separately from the main configuration.

## Configuration Loading and Inheritance

Superconf's configuration loading works seamlessly with inheritance:

```python
class BaseConfig(ContainerConf):
    name = FieldString(default="Base")
    version = FieldString(default="1.0.0")

class DevConfig(BaseConfig):
    debug = FieldBool(default=True)

class ProdConfig(BaseConfig):
    debug = FieldBool(default=False)

# Load configuration based on environment
env = os.environ.get("APP_ENV", "dev")
if env == "prod":
    config = ProdConfig(**config_data)
else:
    config = DevConfig(**config_data)
```

This allows for environment-specific configuration classes with shared base functionality.

## Performance Considerations

Superconf's configuration loading is designed for both flexibility and performance:

- Configuration loading happens once at application startup
- Loaded configurations are cached and reused
- Validation is efficient and focused
- Error handling is clear without sacrificing performance

## Related How-To Guides

For practical applications of configuration loading, see:

- [Loading Configuration from Files](../howto/01_loading_from_files.md)
- [Using Environment Variables](../howto/02_environment_variables.md) 