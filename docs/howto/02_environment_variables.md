# How to Use Environment Variables with Superconf

<div align="center">
  <p><em>Learn how to configure your application using environment variables in Superconf</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">⚡ How-To Guides</a> |
  <a href="01_loading_from_files.md">⏮️ Previous: Loading from Files</a> |
  <a href="03_custom_field_types.md">⏭️ Next: Custom Field Types</a>
</p>

---

This guide shows you how to use environment variables to configure your application with Superconf.

## Basic Environment Variable Loading

Here's a basic example of loading configuration from environment variables:

```python
import os
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp", help="Application name")
    port = FieldInt(default=8000, help="Server port")
    debug = FieldBool(default=False, help="Debug mode")

# Helper function to load from environment
def load_from_env(prefix="APP_"):
    config_data = {}
    
    # Get all environment variables with the prefix
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Remove prefix and convert to lowercase
            config_key = key[len(prefix):].lower()
            config_data[config_key] = value
    
    return AppConfig(**config_data)

# Load configuration from environment variables
config = load_from_env()
print(f"Name: {config.name}")
print(f"Port: {config.port}")
print(f"Debug: {config.debug}")
```

With this approach, you can set environment variables like:
```bash
export APP_NAME="MyService"
export APP_PORT=9000
export APP_DEBUG=true
```

## Creating an Environment Variable Loader

You can create a more robust environment variable loader:

```python
import os
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList
from superconf.configuration import ContainerConf

class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()
    user = FieldString()
    password = FieldString()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    allowed_hosts = FieldList(default=["localhost"])
    database = FieldConf(DatabaseConfig)

class EnvLoader:
    def __init__(self, prefix="APP_"):
        self.prefix = prefix
    
    def load(self, config_class):
        """Load configuration from environment variables"""
        config_data = {}
        
        # Process all environment variables with prefix
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                self._process_env_var(key, value, config_data)
        
        return config_class(**config_data)
    
    def _process_env_var(self, env_key, value, config_data):
        # Remove prefix and convert to lowercase
        key = env_key[len(self.prefix):].lower()
        
        # Handle nested keys (using double underscore as separator)
        if "__" in key:
            parts = key.split("__")
            self._set_nested_value(config_data, parts, value)
        else:
            config_data[key] = value
    
    def _set_nested_value(self, data, key_parts, value):
        """Set value in nested dictionary based on key parts"""
        current = data
        
        # Navigate to the deepest level
        for part in key_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value at the deepest level
        current[key_parts[-1]] = value

# Usage
env_loader = EnvLoader(prefix="APP_")
config = env_loader.load(AppConfig)
```

With this implementation, you can set nested configuration values:
```bash
export APP_NAME="MyService"
export APP_PORT=9000
export APP_DEBUG=true
export APP_ALLOWED_HOSTS="localhost,example.com"
export APP_DATABASE__HOST="db.example.com"
export APP_DATABASE__PORT=5433
export APP_DATABASE__NAME="myapp"
export APP_DATABASE__USER="dbuser"
export APP_DATABASE__PASSWORD="secret"
```

## Environment Variables and Type Casting

Superconf will automatically cast environment variable values to the appropriate types:

```python
import os
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList, FieldDict
from superconf.configuration import ContainerConf

# Set some environment variables for testing
os.environ["APP_NAME"] = "TestApp"
os.environ["APP_PORT"] = "5000"  # String that will be cast to int
os.environ["APP_DEBUG"] = "yes"  # Will be cast to boolean True
os.environ["APP_TAGS"] = "web,api,test"  # Will be cast to list
os.environ["APP_TIMEOUT"] = "30.5"  # Will be cast to float

class AppConfig(ContainerConf):
    name = FieldString()
    port = FieldInt()
    debug = FieldBool()
    tags = FieldList()
    timeout = FieldFloat()

# Load configuration from environment
def load_from_env(prefix="APP_"):
    config_data = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            config_data[config_key] = value
    return AppConfig(**config_data)

config = load_from_env()

# Values are automatically cast to the correct types
print(f"Name: {config.name}, type: {type(config.name)}")  # str
print(f"Port: {config.port}, type: {type(config.port)}")  # int
print(f"Debug: {config.debug}, type: {type(config.debug)}")  # bool
print(f"Tags: {config.tags}, type: {type(config.tags)}")  # list
print(f"Timeout: {config.timeout}, type: {type(config.timeout)}")  # float
```

## Combining Environment Variables with File Configuration

In real-world applications, you'll often want to load configuration from both files and environment variables:

```python
import os
import yaml
from superconf.configuration import ContainerConf
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf

class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()
    user = FieldString()
    password = FieldString()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)

def load_from_file(file_path):
    """Load configuration from YAML file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file) or {}
        return config_data
    return {}

def load_from_env(prefix="APP_"):
    """Load configuration from environment variables"""
    config_data = {}
    
    for key, value in os.environ.items():
        if key.startswith(prefix):
            # Convert APP_DATABASE__HOST to {'database': {'host': value}}
            parts = key[len(prefix):].lower().split("__")
            
            # Navigate to the right level in the config dict
            current = config_data
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Set the value
            current[parts[-1]] = value
    
    return config_data

def load_config(file_path=None, env_prefix="APP_"):
    """Load configuration from file and environment variables"""
    
    # Start with an empty config
    config = AppConfig()
    
    # Load from file if provided
    if file_path:
        file_data = load_from_file(file_path)
        if file_data:
            file_config = AppConfig(**file_data)
            config.merge(file_config)
    
    # Load from environment variables (override file settings)
    env_data = load_from_env(env_prefix)
    if env_data:
        env_config = AppConfig(**env_data)
        config.merge(env_config)
    
    return config

# Usage
config = load_config(file_path="config.yml", env_prefix="APP_")
```

This approach loads configuration from a YAML file first, then overrides with any matching environment variables.

## Environment Variables and Sensitive Data

Environment variables are ideal for sensitive data like passwords and API keys:

```python
import os
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf
from superconf.configuration import ContainerConf

class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()
    user = FieldString()
    password = FieldString()  # Sensitive!
    
class ApiConfig(ContainerConf):
    url = FieldString(default="https://api.example.com")
    key = FieldString()  # Sensitive!
    timeout = FieldInt(default=30)

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)
    api = FieldConf(ApiConfig)

# Load sensitive data from environment
def load_sensitive_data(config):
    """Update sensitive fields from environment variables"""
    # Database password
    if "DB_PASSWORD" in os.environ:
        config.database.password = os.environ["DB_PASSWORD"]
    
    # API key
    if "API_KEY" in os.environ:
        config.api.key = os.environ["API_KEY"]
    
    return config

# Usage
config = AppConfig()
config = load_sensitive_data(config)
```

This allows you to keep sensitive data out of configuration files and version control.

## Command Line Environment Variable Setting

When running your application, you can set environment variables for that specific run:

```bash
# Unix/Linux/macOS
APP_DEBUG=true APP_PORT=9000 python myapp.py

# Windows PowerShell
$env:APP_DEBUG="true"; $env:APP_PORT="9000"; python myapp.py

# Windows Command Prompt
set APP_DEBUG=true && set APP_PORT=9000 && python myapp.py
```

## Environment Files (.env)

For development, you can use a `.env` file to store environment variables:

```python
import os
from dotenv import load_dotenv
from superconf.configuration import ContainerConf
from superconf.fields import FieldString, FieldInt, FieldBool

# Load environment variables from .env file
load_dotenv()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)

# Load from environment
def load_from_env(prefix="APP_"):
    config_data = {}
    for key, value in os.environ.items():
        if key.startswith(prefix):
            config_key = key[len(prefix):].lower()
            config_data[config_key] = value
    return AppConfig(**config_data)

# Usage
config = load_from_env()
```

Example `.env` file:
```
APP_NAME=LocalDev
APP_PORT=3000
APP_DEBUG=true
```

Note: You need to install the `python-dotenv` package:
```bash
pip install python-dotenv
```

## Best Practices

When using environment variables with Superconf:

1. **Use a consistent prefix** for your application's environment variables
2. **Prioritize environment variables** over file configuration for values that change between environments
3. **Always store sensitive data** (passwords, API keys, tokens) in environment variables, not files
4. **Set sensible defaults** in your configuration classes
5. **Use double underscores** (`__`) for nested configuration keys
6. **Document required environment variables** in your application's documentation
7. **Consider validation** of required environment variables early in application startup
8. **Use `.env` files** for development, but not in production

## Complete Example

Here's a complete example that implements all the best practices:

```python
import os
import sys
import yaml
import logging
from dotenv import load_dotenv
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf, FieldList
from superconf.configuration import ContainerConf
from superconf.exceptions import ConfigurationException

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load .env file if it exists (for development)
load_dotenv()

# Configuration classes
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()  # Required
    user = FieldString()  # Required
    password = FieldString()  # Required (sensitive)
    pool_size = FieldInt(default=10)

class ApiConfig(ContainerConf):
    url = FieldString()  # Required
    key = FieldString()  # Required (sensitive)
    timeout = FieldInt(default=30)

class LoggingConfig(ContainerConf):
    level = FieldString(default="info")
    format = FieldString(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    env = FieldString(default="dev")
    debug = FieldBool(default=False)
    port = FieldInt(default=8000)
    allowed_hosts = FieldList(default=["localhost", "127.0.0.1"])
    database = FieldConf(DatabaseConfig)
    api = FieldConf(ApiConfig)
    logging = FieldConf(LoggingConfig)

class ConfigLoader:
    def __init__(self, app_name, env_prefix=None):
        self.app_name = app_name
        self.env_prefix = env_prefix or f"{app_name.upper()}_"
    
    def load_from_file(self, file_path):
        """Load configuration from YAML file"""
        if not os.path.exists(file_path):
            logger.debug(f"Config file not found: {file_path}")
            return {}
        
        try:
            with open(file_path, 'r') as file:
                data = yaml.safe_load(file)
                return data or {}
        except Exception as e:
            logger.warning(f"Error loading config file {file_path}: {e}")
            return {}
    
    def load_from_env(self):
        """Load configuration from environment variables"""
        config_data = {}
        
        for key, value in os.environ.items():
            if key.startswith(self.env_prefix):
                # Remove prefix and convert to lowercase
                clean_key = key[len(self.env_prefix):].lower()
                
                # Handle nested keys
                parts = clean_key.split("__")
                
                # Build nested dict structure
                current = config_data
                for part in parts[:-1]:
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                
                # Set the value at the final level
                current[parts[-1]] = value
        
        return config_data
    
    def load_config(self, config_file=None):
        """Load configuration from file and environment variables"""
        # Start with default config
        config = AppConfig()
        
        # Load from file if provided
        if config_file and os.path.exists(config_file):
            file_data = self.load_from_file(config_file)
            if file_data:
                logger.info(f"Loaded configuration from {config_file}")
                file_config = AppConfig(**file_data)
                config.merge(file_config)
        
        # Load from environment variables (overrides file config)
        env_data = self.load_from_env()
        if env_data:
            logger.info(f"Loaded configuration from environment variables")
            env_config = AppConfig(**env_data)
            config.merge(env_config)
        
        # Validate configuration
        try:
            self.validate_config(config)
        except ConfigurationException as e:
            logger.error(f"Configuration validation failed: {e}")
            raise
        
        return config
    
    def validate_config(self, config):
        """Validate that all required configuration is present"""
        # Check database configuration
        if not config.database.name:
            raise ConfigurationException("Database name is required")
        if not config.database.user:
            raise ConfigurationException("Database user is required")
        if not config.database.password:
            raise ConfigurationException("Database password is required")
        
        # Check API configuration
        if not config.api.url:
            raise ConfigurationException("API URL is required")
        if not config.api.key:
            raise ConfigurationException("API key is required")
        
        # Additional validation based on environment
        if config.env == "prod" and config.debug:
            logger.warning("Debug mode is enabled in production environment")

# Usage
if __name__ == "__main__":
    try:
        # Get config file path from command line args or use default
        config_file = sys.argv[1] if len(sys.argv) > 1 else "config.yml"
        
        # Load configuration
        loader = ConfigLoader(app_name="myapp")
        config = loader.load_config(config_file)
        
        # Use configuration
        logging.basicConfig(level=config.logging.level.upper())
        logger.info(f"Application: {config.name}")
        logger.info(f"Environment: {config.env}")
        logger.info(f"Debug mode: {config.debug}")
        logger.info(f"Database: {config.database.name} on {config.database.host}")
        
    except ConfigurationException as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
```

This example provides a complete configuration system that:

- Loads from both files and environment variables
- Handles sensitive data securely
- Validates required configuration
- Uses a clear naming convention
- Provides helpful error messages
- Supports dotenv for development
``` 