# How to Load Configuration from Files

<div align="center">
  <p><em>Learn how to load Superconf configuration from YAML, JSON, and other file formats</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">⚡ How-To Guides</a> |
  <a href="02_environment_variables.md">⏭️ Next: Environment Variables</a>
</p>

---

This guide shows you how to load configuration from different file formats (YAML, JSON, etc.) in Superconf.

## Basic File Loading

To load configuration from a file, you typically need to:

1. Define your configuration structure
2. Read the file content
3. Parse the content into a Python dictionary
4. Create a configuration instance with the dictionary

Here's a complete example using YAML:

```python
import yaml
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

# Define configuration class
class AppConfig(ContainerConf):
    name = FieldString(default="MyApp", help="Application name")
    port = FieldInt(default=8000, help="Server port")
    debug = FieldBool(default=False, help="Enable debug mode")
    log_level = FieldString(default="info", help="Logging level")

# Load configuration from YAML file
def load_config(file_path):
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    return AppConfig(**config_data)

# Usage
config = load_config('config.yml')
print(f"App name: {config.name}")
print(f"Port: {config.port}")
print(f"Debug mode: {config.debug}")
```

Example `config.yml` file:
```yaml
name: MyAwesomeApp
port: 9000
debug: true
log_level: debug
```

## Using Path Anchors for File Paths

Use Superconf's path anchors to make file paths more flexible:

```python
import yaml
import os
from superconf.anchors import PathAnchor, FileAnchor
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

# Define configuration class
class AppConfig(ContainerConf):
    name = FieldString(default="MyApp", help="Application name")
    port = FieldInt(default=8000, help="Server port")
    debug = FieldBool(default=False, help="Enable debug mode")

# Create path anchors
project_dir = os.path.abspath(os.path.dirname(__file__))
root = PathAnchor(project_dir)
config_dir = PathAnchor("config", parent=root)

# Create file anchors for different environments
default_config = FileAnchor("config.yml", parent=config_dir)
dev_config = FileAnchor("config.dev.yml", parent=config_dir)
prod_config = FileAnchor("config.prod.yml", parent=config_dir)

# Load configuration from file
def load_config(file_anchor):
    config_path = file_anchor.get_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as file:
            config_data = yaml.safe_load(file)
        return AppConfig(**config_data)
    return AppConfig()  # Default config if file doesn't exist

# Load based on environment
env = os.environ.get("APP_ENV", "dev")
if env == "prod":
    config = load_config(prod_config)
elif env == "dev":
    config = load_config(dev_config)
else:
    config = load_config(default_config)
```

## Supporting Multiple File Formats

You can add support for different file formats:

```python
import yaml
import json
import os
from superconf.anchors import FileAnchor
from superconf.configuration import ContainerConf

def load_config_file(file_anchor, config_class):
    """Load configuration from a file with format detection"""
    path = file_anchor.get_path()
    
    if not os.path.exists(path):
        return {}
    
    # Determine format from file extension
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    
    with open(path, 'r') as file:
        if ext == '.json':
            return json.load(file)
        elif ext in ('.yml', '.yaml'):
            return yaml.safe_load(file)
        elif ext == '.toml':
            try:
                import toml
                return toml.load(file)
            except ImportError:
                raise ImportError("toml package is required for .toml files")
        else:
            raise ValueError(f"Unsupported file format: {ext}")

# Usage
def create_config(config_path, config_class):
    file_anchor = FileAnchor(config_path)
    config_data = load_config_file(file_anchor, config_class)
    return config_class(**config_data)
```

## Layered Configuration Files

In real-world applications, you often need to load configuration from multiple files and merge them:

```python
import yaml
import os
from superconf.anchors import PathAnchor, FileAnchor
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf
from superconf.configuration import ContainerConf

# Define configuration structure
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString(default="app")
    user = FieldString()
    password = FieldString()

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)

# Load and merge configuration from multiple files
def load_layered_config():
    # Setup path anchors
    root = PathAnchor(os.path.abspath(os.path.dirname(__file__)))
    config_dir = PathAnchor("config", parent=root)
    
    # Define configuration files in priority order (last overrides earlier)
    config_files = [
        FileAnchor("default.yml", parent=config_dir),
        FileAnchor("config.yml", parent=config_dir),
        FileAnchor(f"config.{os.environ.get('APP_ENV', 'dev')}.yml", parent=config_dir),
        FileAnchor("secrets.yml", parent=config_dir),
    ]
    
    # Start with base configuration
    config = AppConfig()
    
    # Load and merge each file
    for file_anchor in config_files:
        path = file_anchor.get_path()
        if os.path.exists(path):
            print(f"Loading config from: {path}")
            with open(path, 'r') as file:
                config_data = yaml.safe_load(file)
                if config_data:
                    # Create temp config and merge into base
                    temp_config = AppConfig(**config_data)
                    config.merge(temp_config)
    
    return config

# Usage
config = load_layered_config()
```

Example files:
- `default.yml`: Base defaults for all environments
- `config.yml`: Common application settings
- `config.dev.yml`: Development-specific overrides
- `config.prod.yml`: Production-specific overrides
- `secrets.yml`: Sensitive information (not committed to version control)

## Handling Missing Files and Values

Handle missing files and values gracefully:

```python
import yaml
import os
from superconf.configuration import ContainerConf
from superconf.fields import FieldString, FieldInt
from superconf.exceptions import ConfigurationException

class AppConfig(ContainerConf):
    name = FieldString(default="DefaultApp")
    port = FieldInt(default=8000)

def load_config_safely(file_path):
    """Load configuration with error handling"""
    config = AppConfig()  # Start with defaults
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Warning: Config file not found: {file_path}")
        return config
    
    try:
        with open(file_path, 'r') as file:
            config_data = yaml.safe_load(file)
            
        if not config_data:
            print(f"Warning: Empty config file: {file_path}")
            return config
            
        # Create configuration instance with loaded data
        config = AppConfig(**config_data)
        return config
        
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return config
    except ConfigurationException as e:
        print(f"Configuration error: {e}")
        return config
```

## Writing Configuration to Files

You can also save configuration to files:

```python
import yaml
import json
from superconf.configuration import ContainerConf
from superconf.fields import FieldString, FieldInt, FieldBool

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)

def save_config(config, file_path):
    """Save configuration to a file"""
    # Get configuration as a dictionary
    config_dict = {}
    for key in config.keys():
        config_dict[key] = config.get_value(key)
    
    # Determine format from file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    with open(file_path, 'w') as file:
        if ext == '.json':
            json.dump(config_dict, file, indent=2)
        elif ext in ('.yml', '.yaml'):
            yaml.dump(config_dict, file)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

# Usage
config = AppConfig(name="CustomApp", port=9000, debug=True)
save_config(config, "config.yml")
```

## Best Practices

When loading configuration from files:

1. **Use path anchors** to make file paths portable across environments
2. **Layer your configuration** from multiple sources (default → common → environment-specific → local)
3. **Handle errors gracefully** to avoid crashing when files are missing or invalid
4. **Document required configuration** to help users set up their config files
5. **Provide default values** for optional settings
6. **Keep sensitive information** in separate files excluded from version control
7. **Validate configuration** after loading to ensure all required values are present

## Complete Example

Here's a complete example of a robust configuration system:

```python
import os
import yaml
import logging
from superconf.anchors import PathAnchor, FileAnchor
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf
from superconf.configuration import ContainerConf
from superconf.exceptions import ConfigurationException

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define configuration classes
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()  # Required
    user = FieldString()  # Required
    password = FieldString()  # Required

class LoggingConfig(ContainerConf):
    level = FieldString(default="info")
    file = FieldString(default="app.log")
    format = FieldString(default="%(asctime)s - %(levelname)s - %(message)s")

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)
    logging = FieldConf(LoggingConfig)

class ConfigManager:
    def __init__(self, app_name, base_dir=None):
        # Setup path anchors
        if base_dir is None:
            base_dir = os.path.abspath(os.path.dirname(__file__))
        
        self.root = PathAnchor(base_dir, name="root")
        self.config_dir = PathAnchor("config", parent=self.root, name="config_dir")
        
        # Environment settings
        self.app_name = app_name
        self.env = os.environ.get("APP_ENV", "dev")
        
        # Config file anchors
        self.default_config = FileAnchor("default.yml", parent=self.config_dir)
        self.common_config = FileAnchor(f"{app_name}.yml", parent=self.config_dir)
        self.env_config = FileAnchor(f"{app_name}.{self.env}.yml", parent=self.config_dir)
        self.local_config = FileAnchor(f"{app_name}.local.yml", parent=self.config_dir)
        self.secrets_config = FileAnchor("secrets.yml", parent=self.config_dir)
    
    def load_yaml_file(self, file_anchor):
        """Load YAML file if it exists"""
        path = file_anchor.get_path()
        if not os.path.exists(path):
            logger.debug(f"Config file not found: {path}")
            return {}
        
        try:
            with open(path, 'r') as file:
                data = yaml.safe_load(file)
                return data or {}
        except Exception as e:
            logger.warning(f"Error loading config file {path}: {e}")
            return {}
    
    def load_config(self):
        """Load configuration from all sources"""
        # Start with empty config
        config = AppConfig()
        
        # Load configuration layers
        config_files = [
            (self.default_config, "default"),
            (self.common_config, "common"),
            (self.env_config, f"{self.env} environment"),
            (self.local_config, "local"),
            (self.secrets_config, "secrets")
        ]
        
        # Load and merge each config file
        for file_anchor, description in config_files:
            data = self.load_yaml_file(file_anchor)
            if data:
                logger.info(f"Loaded {description} configuration from {file_anchor.get_path()}")
                temp_config = AppConfig(**data)
                config.merge(temp_config)
        
        # Validate configuration
        self.validate_config(config)
        return config
    
    def validate_config(self, config):
        """Ensure all required values are present"""
        try:
            # Access required fields to trigger validation
            db_name = config.database.name
            db_user = config.database.user
            db_password = config.database.password
            
            # Additional custom validation
            if config.debug and self.env == "prod":
                logger.warning("Debug mode is enabled in production environment")
                
        except ConfigurationException as e:
            logger.error(f"Configuration validation failed: {e}")
            raise

# Usage
if __name__ == "__main__":
    manager = ConfigManager("myapp")
    config = manager.load_config()
    
    print(f"App: {config.name}")
    print(f"Environment: {manager.env}")
    print(f"Debug mode: {config.debug}")
    print(f"Database: {config.database.name} on {config.database.host}:{config.database.port}")
```

This example demonstrates a complete configuration system that:
- Loads configuration from multiple files
- Handles missing files gracefully
- Validates required values
- Uses path anchors for portable paths
- Supports different environments 