# Configuration Classes

SuperConf provides three main configuration classes that serve different purposes in managing configuration data:

## Configuration

The base `Configuration` class is the primary class for defining structured configuration objects. It inherits from `ConfigurationDict` and uses the `DeclarativeValuesMetaclass` for handling field declarations.

Key features:
- Declarative style configuration definition
- Field-based configuration with type checking
- Environment variable support through built-in loaders
- Nested configuration support
- Default values and help text support

Example:
```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldBool

class DatabaseConfig(Configuration):
    host = FieldString(default="localhost", help="Database host")
    port = FieldInt(default=5432, help="Database port")
    username = FieldString(help="Database username")
    password = FieldString(help="Database password")

# Usage
db_config = DatabaseConfig()
print(db_config.host)  # "localhost"
print(db_config.port)  # 5432
```

## ConfigurationDict

`ConfigurationDict` is a dictionary-like configuration container that allows dynamic key-value pairs. It's useful when you need to store configurations with arbitrary keys.

Key features:
- Dictionary-like interface
- Dynamic field creation
- Support for nested configurations
- Caching of values
- Environment variable loading
- Extra fields support (enabled by default)

Example:
```python
from superconf.configuration import ConfigurationDict
from superconf.fields import FieldString, FieldInt

class ServiceConfig(ConfigurationDict):
    url = FieldString()
    timeout = FieldInt(default=30)

class AppConfig(ConfigurationDict):
    services = FieldDict(children_class=ServiceConfig)

# Usage
config = AppConfig(values={
    'services': {
        'auth': {'url': 'https://auth.example.com', 'timeout': 60},
        'api': {'url': 'https://api.example.com'},
    }
})

print(config.services['auth'].timeout)  # 60
print(config.services['api'].timeout)   # 30 (default)
```

## ConfigurationList

`ConfigurationList` is a list-like configuration container for managing ordered sequences of configuration items.

Key features:
- List-like interface
- Integer-indexed access
- Support for homogeneous configuration items
- Dynamic field creation for list items
- Environment variable loading
- Extra fields support (enabled by default)

Example:
```python
from superconf.configuration import ConfigurationList
from superconf.fields import FieldString, FieldInt, FieldList

class ServiceConfig(Configuration):
    url = FieldString()
    timeout = FieldInt(default=30)

class AppConfig(Configuration):
    services = FieldList(children_class=ServiceConfig)

# Usage
config = AppConfig(values={
    'services': [
        {'url': 'https://auth.example.com', 'timeout': 60},
        {'url': 'https://api.example.com'},
    ]
})

print(config.services[0].timeout)  # 60
print(config.services[1].timeout)  # 30 (default)
```

## Common Features

All configuration classes share these common features:

1. **Value Loading**:
    - Support for multiple value loaders (Environment variables, dictionaries, etc.)
    - Caching of loaded values
    - Value type casting

2. **Field Management**:
    - Declared fields tracking
    - Dynamic field creation
    - Field value validation

3. **Inheritance Support**:
    - Configuration class inheritance
    - Field inheritance from parent classes
    - Override capability through Meta class

4. **Value Access**:
    - Dictionary-style access (`config['key']`)
    - Attribute-style access (`config.key`)
    - Nested value access (`config.service.url`)
