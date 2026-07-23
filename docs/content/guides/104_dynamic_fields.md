---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Dynamic Dictionary and List Fields

Welcome to the fourth SuperConf tutorial! In this guide, we'll explore dynamic collection fields - `ConfigurationDict` and `ConfigurationList` - which allow you to work with configuration data that has a variable structure.

So far, we've worked with configuration models where every field is predefined in the class. But what if you need to handle configuration with dynamic keys or variable-length collections? For example:

- A list of servers where the number of servers is unknown
- A dictionary of API keys where each key is a service name
- A set of user preferences where users can define their own settings

SuperConf provides powerful tools for handling these dynamic structures while maintaining type safety and validation.

## Understanding Dynamic Fields

Let's first understand why dynamic fields are useful. In a traditional configuration model, every field must be defined in advance:

```python
from superconf import ConfigurationObj, Field

# Traditional configuration with fixed fields
class ServerConfig(ConfigurationObj):
    server1 = Field(default="server1.example.com")
    server2 = Field(default="server2.example.com")
    server3 = Field(default="server3.example.com")
```

But what if you need to support an arbitrary number of servers? That's where dynamic fields come in:

```python
from superconf import ConfigurationDict

# Dynamic configuration with dynamic fields
class ServersConfig(ConfigurationDict):
    class Meta:
        children_class = ServerConfig  # Each item will be a ServerConfig
```

SuperConf provides two special container types to handle these cases:

- `ConfigurationDict`: For handling dictionary-like configuration with variable keys
- `ConfigurationList`: For handling list-like configuration with variable length

The `Meta/children_class` setting is essential for both, as it defines what type of objects will be stored in the collection.

## Dynamic Dictionary Fields

Let's create a configuration model for managing resources, where each resource has a name, type, and location:

```python
from superconf import ConfigurationObj, ConfigurationDict, Field, FieldConf, FieldString

# Define a class for individual resources
class Resource(ConfigurationObj):
    """Individual resource configuration"""
    type = FieldString(default="default", help="Resource type")
    location = FieldString(default="unknown", help="Resource location")
    owner = FieldString(default="admin", help="Resource owner")

# Define a dictionary-like container for resources
class ResourcesConfig(ConfigurationDict):
    """Dictionary of resources"""
    
    class Meta:
        children_class = Resource  # Each item will be a Resource

# Define the main application config
class AppConfig(ConfigurationObj):
    """Main application configuration"""
    app_name = FieldString(default="ResourceManager", help="Application name")
    
    # A dictionary of resources with dynamic keys
    resources = FieldConf(ResourcesConfig, help="Available resources")

# Create an instance with no custom values
app = AppConfig()

# Print the empty resources configuration
print("Empty Resources ConfigurationObj:")
print(f"Resource count: {len(app.resources)}")
print(f"Resources: {app.resources.get_value()}")
```

Notice that we have an empty resources dictionary because we haven't defined any resources yet. Let's add some resources:

```python
# Define some resources
resources_data = {
    "server1": {
        "type": "web",
        "location": "us-east",
        "owner": "team-a"
    },
    "database": {
        "type": "postgres",
        "location": "us-west",
        "owner": "team-b"
    },
    "cache": {
        "type": "redis",
        "location": "eu-central"
        # Owner uses default "admin"
    }
}

# Create a new configuration with resources
app_with_resources = AppConfig(value={"resources": resources_data})

# Print the resources configuration
print("\nResources ConfigurationObj:")
print(f"Resource count: {len(app_with_resources.resources)}")

# Print each resource
print("\nResource Details:")
for name, resource in app_with_resources.resources.items():
    print(f"\nResource: {name}")
    print(f"  Type: {resource.type}")
    print(f"  Location: {resource.location}")
    print(f"  Owner: {resource.owner}")

# Access resources directly
print("\nAccessing resources directly:")
print(f"Server1 type: {app_with_resources.resources.server1.type}")
print(f"Database location: {app_with_resources.resources.database.location}")
print(f"Cache owner: {app_with_resources.resources.cache.owner}")  # Default value

# Check if a resource exists
print("\nChecking resource existence:")
print(f"'server1' exists: {'server1' in app_with_resources.resources}")
print(f"'nonexistent' exists: {'nonexistent' in app_with_resources.resources}")

# Get resource count
resource_count = len(app_with_resources.resources)
print(f"\nTotal resources: {resource_count}")
```

Note:

  * You cannot create a new dict key with attribute assignment
    (`obj.new_key = ...` sets a plain Python attribute).
  * You *can* add keys later with `obj.set_value({"new_key": {...}})` or `merge()`.
  * For lists, `set_value([...])` replaces the whole list; use `merge()` /
    list policies to combine. See
    [106_merge_policies.md](106_merge_policies.md) and
    [merging_configurations.md](../howto/merging_configurations.md).


## Dynamic List Fields

Now let's create a configuration model for a list of servers:

```python
from superconf import ConfigurationList
from superconf.fields import Field, FieldConf, FieldString, FieldInt

# Define a class for server configuration
class ServerConfig(ConfigurationObj):
    """Server configuration"""
    host = FieldString(default="localhost", help="Server hostname")
    port = FieldInt(default=8080, help="Server port")
    role = FieldString(default="worker", help="Server role")

# Define a list-like container for servers
class ServerList(ConfigurationList):
    """List of servers"""
    
    class Meta:
        children_class = ServerConfig  # Each item will be a ServerConfig
        
        # Optional default list of servers
        default = [
            {"host": "primary.example.com", "role": "primary"},
            {"host": "secondary.example.com", "role": "backup"}
        ]

# Define the main application config
class AppConfig(ConfigurationObj):
    """Main application configuration"""
    app_name = FieldString(default="ClusterManager", help="Application name")
    
    # A list of servers
    servers = FieldConf(ServerList, help="Cluster servers")

# Create an instance with default values
app = AppConfig()

# Print the default servers
print("\n\nDefault Servers ConfigurationObj:")
print(f"Server count: {len(app.servers)}")

# Print each server
print("\nDefault Server Details:")
for i, server in enumerate(app.servers):
    print(f"\nServer {i}:")
    print(f"  Host: {server.host}")
    print(f"  Port: {server.port}")
    print(f"  Role: {server.role}")

# Access servers by index
print("\nAccessing servers by index:")
print(f"First server host: {app.servers(0).host}  (access with callable)")
print(f"Second server role: {app.servers[1]['role']}  # [] → value dict")
```

Notes:

  * In the case of list, attribute access can't work since fields must be string and not numbers.

### Customizing the Server List

Now let's create a custom list of servers:

```python
# Define custom servers
servers_data = [
    {
        "host": "web1.example.com",
        "port": 80,
        "role": "web"
    },
    {
        "host": "web2.example.com",
        "port": 80,
        "role": "web"
    },
    {
        "host": "db.example.com",
        "port": 5432,
        "role": "database"
    }
]

# Create a configuration with custom servers
app_with_servers = AppConfig(value={"servers": servers_data})

# Print the custom servers
print("\nCustom Servers ConfigurationObj:")
print(f"Server count: {len(app_with_servers.servers)}")

# Print each server
print("\nCustom Server Details:")
for i, server in enumerate(app_with_servers.servers):
    print(f"\nServer {i}:")
    print(f"  Host: {server.host}")
    print(f"  Port: {server.port}")
    print(f"  Role: {server.role}")

# Check length
server_count = len(app_with_servers.servers)
print(f"\nTotal servers: {server_count}")

# Access by index
print("\nAccessing by index:")
print(f"First server: {app_with_servers.servers(0).host}")
print(f"Second server: {app_with_servers.servers(1).host}")
print(f"Third server: {app_with_servers.servers(2).host}")
```

Note:

  * You cannot create a new list item with attribute assignment.
  * `set_value([...])` replaces the whole list; use `merge()` /
    list policies to combine. See
    [106_merge_policies.md](106_merge_policies.md) and
    [merging_configurations.md](../howto/merging_configurations.md).



## Working with Default Values in Dynamic Fields

You can provide default values for dynamic collections using the `Meta.default` attribute, as we've seen with the `ServerList` example.

Let's create a more detailed example to explore this:

```python
from superconf import Leaf

# Create a configuration class with rich defaults
class RichDefaultsConfig(ConfigurationDict):
    """ConfigurationObj with rich default values"""
    
    class Meta:
        # children_class = ConfigurationObj(extra_fields=True)
        children_class = Leaf
        default = {
            "setting1": {"value": "default1", "enabled": True},
            "setting2": {"value": "default2", "enabled": False},
            "setting3": {"value": "default3", "enabled": True}
        }

# Create an instance
rich_defaults = RichDefaultsConfig()

# Print the default values
print("\n\nRich Default Values:")
print(f"Setting count: {len(rich_defaults)}")

# Print each setting
print("\nDefault Settings:")
for key, setting in rich_defaults.items():
    config = setting.get_value()
    print(f"Setting: {key}")
    print(f"  Value: {config['value']}")
    print(f"  Enabled: {config['enabled']}")

# Override some defaults
custom_settings = {
    "setting1": {"value": "custom1"},  # Only override the value
    "setting4": {"value": "custom4", "enabled": True}  # Add a new setting
}

# Create an instance with custom values
rich_with_customs = RichDefaultsConfig(value=custom_settings)

# Print the combined values
print("\nCombined Default and Custom Values:")
print(f"Setting count: {len(rich_with_customs)}")

# Print each setting
print("\nAll Settings:")
for key, setting in rich_with_customs.items():
    config = setting.get_value()
    print(f"Setting: {key}")
    print(f"  Value: {config['value']}")
    print(f"  Enabled: {config.get('enabled', 'UNSET')}")
```

## Using Dynamic Fields Without Defaults

If you don't provide defaults, dynamic fields will start empty:

```python
from superconf import ConfigurationObj, ConfigurationDict, ConfigurationList
from superconf.fields import FieldConf

# Define simple container classes without defaults
class EmptyDict(ConfigurationDict):
    class Meta:
        children_class = ConfigurationDict

class EmptyList(ConfigurationList):
    class Meta:
        children_class = ConfigurationDict

# Define a config that uses these containers
class EmptyContainersConfig(ConfigurationObj):
    dict_items = FieldConf(EmptyDict)
    list_items = FieldConf(EmptyList)

# Create an instance
empty_containers = EmptyContainersConfig()

# Check if collections are empty
print("\n\nEmpty Containers:")
print(f"Dict items count: {len(empty_containers.dict_items)}")
print(f"List items count: {len(empty_containers.list_items)}")

# Add some items
empty_containers.dict_items.set_value({"item1": {"value": "dict value"}})
empty_containers.list_items.set_value([{"value": "list value"}])

# Check if items were added
print("\nAfter Adding Items:")
print(f"Dict items count: {len(empty_containers.dict_items)}")
print(f"List items count: {len(empty_containers.list_items)}")
print(f"Dict item1 value: {empty_containers.dict_items.item1.value}")
print(f"List item0 value: {empty_containers.list_items(0).value}")

```

## Real-World Example: API Client ConfigurationObj

Let's put everything together in a more realistic example - an API client configuration with multiple endpoints:

```python
from superconf import ConfigurationObj, ConfigurationDict
from superconf.fields import Field, FieldConf, FieldInt, FieldString, FieldBool

# Define the endpoint configuration
class EndpointConfig(ConfigurationObj):
    """ConfigurationObj for an API endpoint"""
    url = FieldString(default="https://api.example.com", help="Endpoint URL")
    timeout = FieldInt(default=30, help="Request timeout in seconds")
    retry = FieldBool(default=True, help="Whether to retry failed requests")
    max_retries = FieldInt(default=3, help="Maximum number of retries")

# Define a dictionary of endpoints
class EndpointsConfig(ConfigurationDict):
    """Dictionary of API endpoints"""
    
    class Meta:
        children_class = EndpointConfig
        
        # Default endpoints
        default = {
            "users": {
                "url": "https://api.example.com/users",
                "timeout": 10
            },
            "products": {
                "url": "https://api.example.com/products",
                "timeout": 20
            }
        }

# Define the main API client configuration
class ApiClientConfig(ConfigurationObj):
    """API client configuration"""
    base_url = FieldString(default="https://api.example.com", help="Base API URL")
    auth_token = FieldString(default="", help="Authentication token")
    debug = FieldBool(default=False, help="Enable debug mode")
    
    # Dictionary of endpoints
    endpoints = FieldConf(EndpointsConfig, help="API endpoints")

# Create the configuration
api_config = ApiClientConfig()

# Print the configuration
print("\n\nAPI Client ConfigurationObj:")
print(f"Base URL: {api_config.base_url}")
print(f"Auth Token: {api_config.auth_token}")
print(f"Debug Mode: {api_config.debug}")

# Print the endpoints
print("\nDefault Endpoints:")
for name, endpoint in api_config.endpoints.items():
    print(f"\nEndpoint: {name}")
    print(f"  URL: {endpoint.url}")
    print(f"  Timeout: {endpoint.timeout}")
    print(f"  Retry: {endpoint.retry}")
    print(f"  Max Retries: {endpoint.max_retries}")

# Add a new endpoint via set_value (attribute assignment would not create a child)
api_config.endpoints.set_value({
    "orders": {
        "url": "https://api.example.com/orders",
        "timeout": 15,
        "retry": True,
        "max_retries": 5,
    }
})

# Print the updated endpoints
print("\nUpdated Endpoints:")
for name, endpoint in api_config.endpoints.items():
    print(f"  - {name}: {endpoint.url}")
```

## Summary

In this guide, we've learned:

- How to use `ConfigurationDict` and `ConfigurationList` for dynamic fields
- How to configure the `children_class` attribute to define the structure of items
- How to access, iterate, and check membership in dynamic collections
- How to provide default values for dynamic collections
- How to add items dynamically to dynamic collections
- How dynamic fields behave when no defaults are provided
- How to apply these concepts in a realistic API client configuration

Dynamic fields are a powerful feature of SuperConf that allow you to work with dynamic configuration structures while maintaining type safety and validation.

## Try It Yourself

Here are some exercises to practice what you've learned:

1. Create a configuration for a web application with a dynamic dictionary of routes, where each route has a path, handler, and HTTP method.
2. Create a configuration for a database connection pool with a dynamic list of database connections, each with its own host, port, username, and password.
3. Experiment with nested dynamic structures, such as a dictionary of services, each containing a list of endpoints.
4. Create a configuration with default values, override some values, and add new values dynamically.
5. Practice iterating over dynamic collections and accessing items by key or index. 

```python

```
