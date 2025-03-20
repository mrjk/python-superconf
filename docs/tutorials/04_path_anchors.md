# Working with Path Anchors

This tutorial covers how to use Superconf's path anchoring system to create flexible, portable path references for configuration files and directories.

## Understanding Path Anchors

Path anchors in Superconf help you manage file and directory paths, making them adaptable to different environments and project structures. The key components are:

- `PathAnchor`: Base class for handling directory paths with parent points
- `FileAnchor`: Extension of PathAnchor for handling file paths specifically

## Basic Path Anchoring

Let's start with a simple example of path anchoring:

```python
from superconf.anchors import PathAnchor, FileAnchor, REL, ABS

# Create a root anchor at a specific directory
project_dir = "/home/user/myproject"
root = PathAnchor(project_dir)

# Create a config directory anchor relative to the root
config_dir = PathAnchor("config", parent=root)

# Create a file anchor in the config directory
config_file = FileAnchor("settings.yml", parent=config_dir)

# Get the absolute path to the config file
print(config_file.get_path())  # /home/user/myproject/config/settings.yml

# Get the path relative to the current directory
print(config_file.get_path(mode=REL))  # path/to/config/settings.yml (depends on current dir)
```

## Path Resolution Modes

Path anchors support different resolution modes:

- `ABS` (or `"abs"`): Resolve to absolute paths
- `REL` (or `"rel"`): Resolve to relative paths (from current working directory)

```python
# Create anchors
project_dir = "/home/user/myproject"
root = PathAnchor(project_dir)
data_dir = PathAnchor("data", parent=root)

# Get paths in different modes
abs_path = data_dir.get_path(mode=ABS)  # /home/user/myproject/data
rel_path = data_dir.get_path(mode=REL)  # path/to/data (relative to current dir)

# Set the default mode for an anchor
logs_dir = PathAnchor("logs", parent=root, mode=REL)
print(logs_dir.get_path())  # Always returns relative path by default
print(logs_dir.get_path(mode=ABS))  # Can still get absolute path when needed
```

## Working with File Anchors

`FileAnchor` extends `PathAnchor` to handle file paths with more convenience methods:

```python
from superconf.anchors import PathAnchor, FileAnchor

# Create directory and file anchors
project_dir = "/home/user/myproject"
root = PathAnchor(project_dir)
config_dir = PathAnchor("config", parent=root)

# Create a file anchor
config_file = FileAnchor("settings.yml", parent=config_dir)

# Get the full file path
print(config_file.get_path())  # /home/user/myproject/config/settings.yml

# Get just the directory part
print(config_file.get_dir())   # /home/user/myproject/config

# Get just the filename
print(config_file.filename)  # settings.yml
```

You can also create a file anchor directly with a full path:

```python
# Create a file anchor with a full path
config_file = FileAnchor("/home/user/myproject/config/settings.yml")

# Or with separate directory and filename
config_file = FileAnchor(
    directory="/home/user/myproject/config",
    filename="settings.yml"
)
```

## Path Cleaning and Normalization

Path anchors can automatically clean and normalize paths:

```python
# Create an anchor with a path that needs normalization
root = PathAnchor("/home/user/myproject")
messy_path = PathAnchor("data/../config/./settings", parent=root)

# Get the clean path
print(messy_path.get_path(clean=True))  # /home/user/myproject/config/settings

# Create an anchor with built-in cleaning
clean_path = PathAnchor(
    "data/../config/./settings",
    parent=root,
    clean=True  # Always clean when getting paths
)
print(clean_path.get_path())  # /home/user/myproject/config/settings
```

## Complex Path Hierarchies

You can create complex path hierarchies by chaining anchors:

```python
# Create a project structure
project_dir = "/home/user/myproject"
root = PathAnchor(project_dir)

# App directories
app_dir = PathAnchor("app", parent=root)
config_dir = PathAnchor("config", parent=app_dir)
data_dir = PathAnchor("data", parent=app_dir)

# Data files
user_data = FileAnchor("users.json", parent=data_dir)
product_data = FileAnchor("products.json", parent=data_dir)

# Config files
settings = FileAnchor("settings.yml", parent=config_dir)
secrets = FileAnchor("secrets.yml", parent=config_dir)

# Print paths
print(f"App directory: {app_dir.get_path()}")
print(f"Config directory: {config_dir.get_path()}")
print(f"Settings file: {settings.get_path()}")
print(f"User data file: {user_data.get_path()}")
```

## Practical Example: Configuration File Management

Here's a practical example of using path anchors to manage configuration files:

```python
from superconf.anchors import PathAnchor, FileAnchor
from superconf.fields import FieldString, FieldConf
from superconf.configuration import ContainerConf
import os
import yaml

# Define project directory structure
home_dir = os.path.expanduser("~")
project_dir = os.path.join(home_dir, "myproject")

# Create path anchors
root = PathAnchor(project_dir)
config_dir = PathAnchor("config", parent=root)
data_dir = PathAnchor("data", parent=root)

# Create file anchors for configuration files
main_config = FileAnchor("config.yml", parent=config_dir)
dev_config = FileAnchor("config.dev.yml", parent=config_dir)
prod_config = FileAnchor("config.prod.yml", parent=config_dir)

# Configuration class
class AppConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    data_path = FieldString()
    log_path = FieldString()

# Helper function to load config from a file
def load_config_from_file(file_anchor):
    config_path = file_anchor.get_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

# Load configuration based on environment
env = os.environ.get("APP_ENV", "dev")
if env == "prod":
    config_file = prod_config
elif env == "dev":
    config_file = dev_config
else:
    config_file = main_config

# Create configuration with values from file
config_values = load_config_from_file(config_file)
app_config = AppConfig(**config_values)

# Resolve data and log paths relative to project root
app_config.data_path = PathAnchor(app_config.data_path, parent=root).get_path()
app_config.log_path = PathAnchor(app_config.log_path, parent=root).get_path()

print(f"App name: {app_config.app_name}")
print(f"Data path: {app_config.data_path}")
print(f"Log path: {app_config.log_path}")
```

## Named Anchors

You can give your anchors names to make them easier to identify:

```python
# Create named anchors
root = PathAnchor("/home/user/myproject", name="project_root")
config = PathAnchor("config", parent=root, name="config_dir")
data = PathAnchor("data", parent=root, name="data_dir")

# The name is used in the string representation
print(root)  # <project_root /home/user/myproject>
print(config)  # <config_dir [/home/user/myproject]config>

# Get the name of an anchor
print(root.name)  # project_root
print(config.name)  # config_dir
```

## Path Anchors and Configuration Integration

You can integrate path anchors with configuration classes:

```python
from superconf.anchors import PathAnchor, FileAnchor
from superconf.fields import FieldString, FieldBool
from superconf.configuration import ContainerConf
import os

# Define the project structure
project_dir = os.path.abspath(os.path.dirname(__file__))
root = PathAnchor(project_dir, name="project_root")
config_dir = PathAnchor("config", parent=root, name="config_dir")
data_dir = PathAnchor("data", parent=root, name="data_dir")
logs_dir = PathAnchor("logs", parent=root, name="logs_dir")

# Define configuration with paths
class PathConfig(ContainerConf):
    project_root = FieldString(default=root.get_path())
    config_path = FieldString(default=config_dir.get_path())
    data_path = FieldString(default=data_dir.get_path())
    logs_path = FieldString(default=logs_dir.get_path())
    create_dirs = FieldBool(default=True)
    
    def init(self):
        """Initialize directory structure"""
        if self.create_dirs:
            for path in [self.config_path, self.data_path, self.logs_path]:
                if not os.path.exists(path):
                    os.makedirs(path)
            return True
        return False

# Create and initialize configuration
path_config = PathConfig()
created = path_config.init()
print(f"Directories created: {created}")
print(f"Project root: {path_config.project_root}")
print(f"Config path: {path_config.config_path}")
print(f"Data path: {path_config.data_path}")
print(f"Logs path: {path_config.logs_path}")
```

## Next Steps

Now that you understand how to work with path anchors in Superconf, you can explore more advanced topics:

- Custom field types with path validation
- Loading configuration from different file formats
- Creating dynamic configuration structures
- Implementing environment-specific configuration 