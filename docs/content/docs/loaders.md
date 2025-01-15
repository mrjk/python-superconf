# Configuration Loaders

SuperConf provides several loader classes that allow you to load configuration values from different sources. Each loader implements a consistent interface for retrieving configuration values.

## Available Loaders

### 1. Environment Loader

The `Environment` loader retrieves configuration values from environment variables. It supports optional prefixing of environment variable names.

```python
from superconf.loaders import Environment, EnvPrefix

# Without prefix
config = Configuration(loaders=[Environment()])

# With prefix
config = Configuration(loaders=[Environment(keyfmt=EnvPrefix("MYAPP_"))])
```

Environment variables will be automatically converted to uppercase. With a prefix:
- Configuration key: `database_url`
- Environment variable: `MYAPP_DATABASE_URL`

### 2. EnvFile Loader

The `EnvFile` loader reads configuration from a `.env` file. It supports the standard environment file format.

```python
from superconf.loaders import EnvFile

config = Configuration(loaders=[EnvFile(filename=".env")])
```

Example `.env` file:
```
DATABASE_URL=postgresql://localhost:5432/mydb
API_KEY=secret123
DEBUG=true
```

### 3. CommandLine Loader

The `CommandLine` loader extracts configuration from command-line arguments using Python's `argparse`.

```python
from superconf.loaders import CommandLine
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--host', default='localhost')
parser.add_argument('--port', type=int, default=8000)

config = Configuration(loaders=[CommandLine(parser)])
```

### 4. Dict Loader

The `Dict` loader allows you to provide configuration values directly through a Python dictionary.

```python
from superconf.loaders import Dict

config_dict = {
    'database': {
        'host': 'localhost',
        'port': 5432
    },
    'debug': True
}

config = Configuration(loaders=[Dict(config_dict)])
```

### 5. RecursiveSearch Loader

The `RecursiveSearch` loader searches for configuration files in the current directory and parent directories until it reaches a specified root path.

```python
from superconf.loaders import RecursiveSearch

config = Configuration(loaders=[
    RecursiveSearch(
        starting_path="./myapp",
        root_path="/",
        filetypes=[
            ("*.ini", IniFileLoader),
            ("*.yaml", YamlFileLoader)
        ]
    )
])
```

## Loader Priority

When multiple loaders are specified, they are checked in order. The first loader that provides a value for a configuration key will be used. This allows for a flexible override system:

```python
config = Configuration(loaders=[
    Environment(),           # Highest priority: environment variables
    EnvFile(".env"),        # Then .env file
    Dict(default_config)    # Lowest priority: default values
])
```

## Common Loader Features

All loaders in SuperConf share these common characteristics:

1. **Consistent Interface**:
   - `__contains__(item)`: Check if a configuration key exists
   - `__getitem__(item)`: Retrieve a configuration value
   - `check()`: Verify if the loader is usable
   - `reset()`: Clear any cached values

2. **Error Handling**:
   - Raises `KeyError` when a configuration key is not found
   - Raises `InvalidConfigurationFile` for file-based loaders when the file is invalid
   - Raises `InvalidPath` when file paths are incorrect

3. **Type Casting**:
   - Raw values are returned as strings
   - Type casting is handled at the configuration field level
   - Boolean values are automatically detected and converted

## Creating Custom Loaders

You can create custom loaders by inheriting from `AbstractConfigurationLoader`:

```python
from superconf.loaders import AbstractConfigurationLoader

class MyCustomLoader(AbstractConfigurationLoader):
    def __init__(self, source):
        self.source = source

    def __contains__(self, item):
        return item in self.source

    def __getitem__(self, item):
        return self.source[item]

    def check(self):
        return True  # Implement your validation logic

    def reset(self):
        # Implement if you need to clear cached data
        pass
```
