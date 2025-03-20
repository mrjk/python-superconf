# Introduction to Superconf

Superconf is a flexible configuration management library for Python that provides hierarchical configuration with strong typing, path resolution, and extensible configuration sources.

## What is Superconf?

Superconf helps you manage configuration data in Python applications with a focus on:

- **Type safety**: Define the expected types for configuration values
- **Hierarchical configuration**: Organize configs in nested structures
- **Configuration inheritance**: Share settings across related components
- **Path anchoring**: Resolve paths relative to different base directories
- **Flexible value resolution**: Support for multiple configuration sources

## Installation

```bash
pip install superconf
```

## Basic Usage

Here's a simple example to get you started with Superconf:

```python
from superconf.fields import FieldInt, FieldString, FieldBool
from superconf.configuration import ContainerConf

# Define a configuration class
class AppConfig(ContainerConf):
    debug = FieldBool(default=False, help="Enable debug mode")
    port = FieldInt(default=8000, help="Server port")
    host = FieldString(default="localhost", help="Server host")

# Create an instance with default values
config = AppConfig()

# Access configuration values
print(f"Server running at: {config.host}:{config.port}")
print(f"Debug mode: {config.debug}")

# Override values
config_dev = AppConfig(debug=True, port=3000)
print(f"Dev server running at: {config_dev.host}:{config_dev.port}")
print(f"Debug mode: {config_dev.debug}")
```

## Key Components

Superconf has several key components that work together:

1. **Fields**: Define the structure and types of your configuration
2. **Containers**: Group related configuration fields together
3. **Casting**: Convert configuration values to appropriate types
4. **Path Anchors**: Handle path resolution for file-based configurations

In the following tutorials, we'll explore each of these components in depth and show you how to use Superconf effectively in your applications.

## When to Use Superconf

Superconf is particularly useful when:

- You need to manage complex application configuration
- You want strong typing and validation for configuration values
- Your configuration needs to be loaded from multiple sources
- You need to work with file paths that can vary between environments
- You want to share configuration between different components

## Next Steps

Continue to the next tutorial to learn how to define configuration classes and work with different field types. 