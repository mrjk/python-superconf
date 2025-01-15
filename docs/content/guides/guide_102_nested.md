# Nested Configuration Guide

## 1. Basic Nested Configurations of configurations

This guide explains how to work with nested configurations in SuperConf, which is useful for organizing complex configuration structures.

The most common way to create nested configurations is by defining separate configuration classes:

```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldBool

class DatabaseConfig(Configuration):
    host = FieldString(default="localhost", help="Database host")
    port = FieldInt(default=5432, help="Database port")
    username = FieldString(help="Database username")
    password = FieldString(help="Database password")

class RedisConfig(Configuration):
    host = FieldString(default="localhost", help="Redis host")
    port = FieldInt(default=6379, help="Redis port")
    db = FieldInt(default=0, help="Redis database number")

class AppConfig(Configuration):
    debug = FieldBool(default=False, help="Enable debug mode")
    database = DatabaseConfig
    redis = RedisConfig

# Example 1: Using default values
config = AppConfig()
print(config.debug)              # False (default value)
print(config.database.host)      # "localhost" (default value)
print(config.redis.port)         # 6379 (default value)
print(config.database.username)  # None (no default value)
print(config.is_set('database.username'))  # False

# Example 2: Overriding some values
config = AppConfig(values={
    'debug': True,
    'database': {
        'host': 'db.example.com',
        'username': 'admin'
    }
})
print(config.debug)              # True (overridden)
print(config.database.host)      # "db.example.com" (overridden)
print(config.database.port)      # 5432 (still default)
print(config.database.username)  # "admin" (set value)
print(config.redis.host)         # "localhost" (default value)
```


## 2. Deep Nesting

You can nest configurations as deeply as needed:

```python
class LoggingConfig(Configuration):
    level = FieldString(default="INFO")
    format = FieldString(default="%(levelname)s: %(message)s")

class ServiceConfig(Configuration):
    url = FieldString(help="Service URL")
    timeout = FieldInt(default=30)
    logging = LoggingConfig

class AppConfig(Configuration):
    name = FieldString(default="myapp")
    service_a = ServiceConfig
    service_b = ServiceConfig
```

Accessing Nested Values:

```python
config = AppConfig()
print(config.service_a.logging.level)  # "INFO"
print(config.is_set('service_a.url'))  # False (required field not set)
```

## 4. Dynamic Field Configurations

For cases where you need to handle configurations with unknown fields or dynamic structures, SuperConf provides the `FieldConf` field type with the `children_class` parameter.



```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldConf

class ServiceConfig(Configuration):
    url = FieldString()
    timeout = FieldInt(default=30)

class DynamicConfig(Configuration):
    # Will accept any number of services as key-value pairs
    services_as_dict = FieldDict(children_class=ServiceConfig)
    services_as_list = FieldList(children_class=ServiceConfig)

# Usage example
config = DynamicConfig(values={
    'services_as_dict': {
        'auth': {'url': 'https://auth.example.com', 'timeout': 60},
        'api': {'url': 'https://api.example.com'},
        'cache': {'url': 'https://cache.example.com', 'timeout': 15}
    },
    'services_as_list': [
        {'url': 'https://auth.example.com', 'timeout': 60},
        {'url': 'https://api.example.com'},
        {'url': 'https://cache.example.com', 'timeout': 15}
    ]
})

print(config.services_as_dict['auth'].timeout)  # 60
print(config.services_as_dict['api'].timeout)   # 30 (default value)
print(config.services_as_dict['cache'].url)     # "https://cache.example.com"

print(config.services_as_list[0].timeout)  # 60
print(config.services_as_list[1].timeout)   # 30 (default value)
print(config.services_as_list[2].url)     # "https://cache.example.com"
```




## 5. Dynamic Field Configurations with custom classes

### Dictionary of Configurations

To create a dictionary of configuration objects with dynamic keys:

```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldConf

class ServiceConfig(Configuration):
    url = FieldString()
    timeout = FieldInt(default=30)

class DynamicConfig(Configuration):
    # Will accept any number of services as key-value pairs
    services = FieldConf(children_class=ServiceConfig)

# Usage example
config = DynamicConfig(values={
    'services': {
        'auth': {'url': 'https://auth.example.com', 'timeout': 60},
        'api': {'url': 'https://api.example.com'},
        'cache': {'url': 'https://cache.example.com', 'timeout': 15}
    }
})

print(config.services['auth'].timeout)  # 60
print(config.services['api'].timeout)   # 30 (default value)
print(config.services['cache'].url)     # "https://cache.example.com"
```

### List of Configurations

For handling lists of configuration objects:

```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf

class EndpointConfig(Configuration):
    host = FieldString()
    port = FieldInt(default=80)
    secure = FieldBool(default=False)

class LoadBalancerConfig(ConfigurationList):
    # Will accept a list of endpoints
    endpoints = FieldConf(children_class=EndpointConfig)

# Usage example
config = LoadBalancerConfig(values=[
        {'host': 'server1.example.com', 'port': 443, 'secure': True},
        {'host': 'server2.example.com'},
        {'host': 'server3.example.com', 'port': 8080}
    ]
)

print(config.endpoints[0].secure)  # True
print(config.endpoints[1].port)    # 80 (default value)
print(config.endpoints[2].host)    # "server3.example.com"
```

The `FieldConf` with `children_class` maintains all the benefits of SuperConf's type checking, validation, and environment variable support while providing flexibility for dynamic configurations. Use `is_list=True` when you need a list of configurations, and omit it for dictionary-style configurations.

