# Nested Configuration Structures

Welcome to the third SuperConf tutorial! In this guide, we'll explore how to create and work with nested configuration structures.

Many real-world applications require hierarchical configuration data. For example, you might need to group related settings for databases, servers, logging, and more. SuperConf makes it easy to model these hierarchical structures using the `FieldConf` field type.

## Understanding Configuration Hierarchies

Let's first understand what a hierarchical configuration looks like. Imagine a web application configuration with server, database, and logging sections:

```yaml
# Example of hierarchical configuration in YAML
app:
  server:
    host: "localhost"
    port: 8080
  database:
    url: "postgresql://localhost/mydb"
    pool_size: 10
  logging:
    level: "info"
    file: "/var/log/app.log"
```

With SuperConf, you can model this structure in Python, providing type safety, validation, and easy access to nested values.

## Defining Nested Configuration Models

Let's create a nested configuration model for our web application:

```python
from superconf import ConfigurationObj, Field, FieldConf, FieldInt, FieldString

# Define the server configuration
class ServerConfig(ConfigurationObj):
    """Server configuration"""
    host = FieldString(default="localhost", help="Server hostname")
    port = FieldInt(default=8080, help="Server port")

# Define the database configuration
class DatabaseConfig(ConfigurationObj):
    """Database configuration"""
    url = FieldString(default="postgresql://localhost/mydb", help="Database URL")
    pool_size = FieldInt(default=5, help="Connection pool size")
    timeout = FieldInt(default=30, help="Connection timeout in seconds")

# Define the logging configuration
class LoggingConfig(ConfigurationObj):
    """Logging configuration"""
    level = FieldString(default="info", help="Logging level")
    file = FieldString(default="/var/log/app.log", help="Log file path")
    
# Define the main application configuration
class AppConfig(ConfigurationObj):
    """Main application configuration"""
    app_name = FieldString(default="MyApp", help="Application name")
    debug = Field(default=False, help="Enable debug mode")
    
    # Nested configurations
    server = FieldConf(ServerConfig, help="Server configuration")
    database = FieldConf(DatabaseConfig, help="Database configuration")
    logging = FieldConf(LoggingConfig, help="Logging configuration")

# Create an instance with default values
app = AppConfig()

# Print the configuration structure
print("Application Configuration Structure:")
print(f"\nApp Name: {app.app_name}")
print(f"Debug Mode: {app.debug}")

print("\nServer Configuration:")
print(f"  Host: {app.server.host}")
print(f"  Port: {app.server.port}")

print("\nDatabase Configuration:")
print(f"  URL: {app.database.url}")
print(f"  Pool Size: {app.database.pool_size}")
print(f"  Timeout: {app.database.timeout}")

print("\nLogging Configuration:")
print(f"  Level: {app.logging.level}")
print(f"  File: {app.logging.file}")
```

In this example, we've created nested configuration classes for each section of our application. The main `AppConfig` class includes these nested configurations using `FieldConf`.

## Working with Nested Configurations

Now let's see how we can work with these nested configurations in practice.

### Creating an Instance with Custom Values

In real applications, you'll want to customize the configuration. You can do this by providing a nested dictionary structure:

```python
# Create a configuration with custom values
custom_config = {
    "app_name": "CustomApp",
    "debug": True,
    "server": {
        "host": "0.0.0.0",
        "port": 9000
    },
    "database": {
        "url": "postgresql://db.example.com/custom",
        "pool_size": 10
        # Notice we're not overriding timeout, it will use the default
    },
    "logging": {
        "level": "debug"
        # Notice we're not overriding file, it will use the default
    }
}

# Create the application config with custom values
app = AppConfig(value=custom_config)

# Print the customized configuration
print("\n\nCustomized Application Configuration:")
print(f"\nApp Name: {app.app_name}")
print(f"Debug Mode: {app.debug}")

print("\nServer Configuration:")
print(f"  Host: {app.server.host}")
print(f"  Port: {app.server.port}")

print("\nDatabase Configuration:")
print(f"  URL: {app.database.url}")
print(f"  Pool Size: {app.database.pool_size}")
print(f"  Timeout: {app.database.timeout} (using default)")

print("\nLogging Configuration:")
print(f"  Level: {app.logging.level}")
print(f"  File: {app.logging.file} (using default)")

# Verify values were set correctly
assert app.app_name == "CustomApp"
assert app.debug is True
assert app.server.host == "0.0.0.0"
assert app.server.port == 9000
assert app.database.url == "postgresql://db.example.com/custom"
assert app.database.pool_size == 10
assert app.database.timeout == 30  # Default value
assert app.logging.level == "debug"
assert app.logging.file == "/var/log/app.log"  # Default value

print("\nAll custom values are correctly set!")
```

We can have a global overview with `get_value()`:

```python
from pprint import pprint

pprint(app.get_value())
```

Notice how we can override only the values we need to change, and the rest will use their default values.

## Understanding Leaf vs Container Fields

SuperConf has two main types of fields:

- **Leaf Fields**: Store simple values (strings, numbers, booleans, etc.). They are leaf nodes.
- **Container Fields**: Store complex nested structures like dictionaries or other configuration objects. They can contains other containers or leafs nodes.

`FieldConf` is a container field that holds another configuration object. Understanding the difference between leaf and container fields is important because they behave differently when accessed.

Let's create a simple example to demonstrate the difference:

```python
from superconf import ConfigurationObj, Field, FieldConf

# Define a simple nested configuration
class NestedConfig(ConfigurationObj):
    value = Field(default="nested value")

class RootConfig(ConfigurationObj):
    # Leaf field
    leaf = Field(default="leaf value")
    
    # Container field
    container = FieldConf(NestedConfig)

# Create an instance
config = RootConfig()

print("Leaf vs Container Fields:")
print("\nLeaf Field:")
print(f"  Value: {config.leaf}")
print(f"  Type: {type(config.leaf)}")

print("\nContainer Field:")
print(f"  Value: {config.container.value}")
print(f"  Type: {type(config.container)}")
print(f"  Container's value field type: {type(config.container.value)}")
```

## Accessing Nested Configurations

SuperConf provides multiple ways to access nested configuration values, similar to how we access simple fields.

### 1. Attribute Access (Value or Node)

The most natural way to access nested values is through attribute access. It provides some auto-magic resolution, it returns the value if if the node is a `Leaf`, or the container object otherwise:

```python
# Using attribute access to get values
print("Accessing nested values through attributes:")
server_host = app.server.host
db_url = app.database.url
log_level = app.logging.level

print(f"  Server Host: {server_host}")
print(f"  Database URL: {db_url}")
print(f"  Logging Level: {log_level}")
```

As explained above, when you target a container, then the container is returned instead of the value:

```python
# Using attribute access to get container nodes
print("Accessing nested containers through attributes:")
server_node = app.server
db_node = app.database
logging_node = app.logging

print(f"  Server Host: {server_node}")
print(f"  Database URL: {db_node}")
print(f"  Logging Level: {logging_node}")
```

### 2. Dictionary-Style Access (always Value)

You can also use dictionary-style access, which is useful when the field name is dynamic:

```python
# Using dictionary-style access
print("\nAccessing nested values through dictionary-style access:")
server_host = app["server"]["host"]
db_url = app["database"]["url"]
log_level = app["logging"]["level"]

print(f"  Server Host: {server_host}")
print(f"  Database URL: {db_url}")
print(f"  Logging Level: {log_level}")

# This is particularly useful when the field name is in a variable
section_name = "server"
field_name = "port"
value = app[section_name][field_name]
print(f"Dynamic access to {section_name}.{field_name}: {value}")
```

Accessing items through the dictionnary-style access always return the value:

```python
# Using attribute access to get container nodes
print("Accessing nested containers through attributes:")
server_node = app.server
db_node = app.database
logging_node = app.logging

print(f"  Server Host: {app.server}")
print(f"  Server Host: {app['server']}")
print(f"  Database URL: {app['database']}")
print(f"  Logging Level: {app['logging']}")
```

### 3. Call Access (always Node)


```python
# Using attribute access to get container nodes
print("Accessing nested containers through attributes:")
server_node = app.server
db_node = app.database
logging_node = app.logging

print(f"  Server Host: {app.server}")
print(f"  Server Host: {app('server')}")
print(f"  Database URL: {app('database')}")
print(f"  Logging Level: {app('logging')}")
```

## Getting All Values

To get all values from a configuration as a nested dictionary, including nested ones, use the `get_value()` method:

```python
from pprint import pprint

# Get all values as a nested dictionary
print("\nGetting all values as a nested dictionary:")
all_config = app.get_value()
pprint(all_config)

# We can verify the structure
assert all_config["app_name"] == "CustomApp"
assert all_config["debug"] is True
assert all_config["server"]["host"] == "0.0.0.0"
assert all_config["server"]["port"] == 9000
assert all_config["database"]["url"] == "postgresql://db.example.com/custom"
```

## Working with Default Values in Nested Configurations

You can access default values for nested configurations using the `get_default()` method:

```python
# Get default values for nested fields
print("\nAccessing default values in nested configurations:")

server_obj = app("server")
server_host_obj = server_obj("host")

# Get the default value
default_host = server_host_obj.get_default()
print(f"Default value for server.host: {default_host}")

# Get the actual value
actual_host = server_host_obj.get_value()
print(f"Actual value for server.host: {actual_host}")

# Compare with the main config's default
app_default = AppConfig()
print(f"Default from fresh instance: {app_default.server.host}")
```

## Modifying Nested Configuration Values

You can modify nested configuration values just like you would with simple fields:

```python
# Modify a nested configuration value
print("\nModifying nested configuration values:")
print(f"Before: app.server.port = {app.server.port}")

app.server.port = 8888

print(f"After: app.server.port = {app.server.port}")

# You can also use dictionary-style access
app["database"]["pool_size"] = 20
print(f"Modified database.pool_size = {app.database.pool_size}")

# Or use set_value
app.logging.set_value("level", "warning")
print(f"Modified logging.level = {app.logging.level}")


```

## Summary

In this guide, we've learned:

- How to define nested configuration structures using `FieldConf`
- The difference between leaf fields and container fields
- Various ways to access nested configuration values
- How to use special dunder methods to access values and objects
- How to get all values from a configuration, including nested ones
- How to access and modify nested configuration values

Nested configurations are a powerful feature of SuperConf that allow you to model complex, hierarchical configuration data in a structured and type-safe way.

## Try It Yourself

Here are some exercises to practice what you've learned:

1. Create a configuration model for a web application with nested sections for frontend, backend, and security settings.
2. Create an instance with custom values for some (but not all) nested settings and verify that default values are used for the rest.
3. Try accessing nested values using different methods and observe the differences.
4. Modify some nested values and verify that the changes were applied correctly.
5. Create a deeply nested configuration (3+ levels) and practice accessing values at different levels. 

```python

```
