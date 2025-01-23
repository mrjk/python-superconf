# Quickstart

## 1. Import Required Modules

```python
from superconf.configuration import Configuration
from superconf.fields import FieldConf
```

## 2. Define Your Configuration

Here's a basic example of defining a configuration class:

```python
class AppConfig(Configuration):
    """Application configuration"""
    
    class Meta:
        cache = True
        app_name = "my-app"
        env_prefix = "MYAPP"
    
    # Define configuration fields
    root_dir = FieldConf(help_text="Root directory for the application")
    module_dir = FieldConf(help_text="Directory for modules")
    data_dir = FieldConf(help_text="Directory for data storage")

class App(Configuration):
    """Main Application example"""
    
    class Meta:
        cache = True
        app_name = "my-app"
        env_prefix = "MYAPP"
    
    # Application configuration
    config = FieldConf(children_class=AppConfig)
    
    @property
    def root_dir(self):
        """Return root dir"""
        return self.config.root_dir
    
    @property
    def module_dir(self):
        """Return module dir"""
        return self.config.module_dir
    
    @property
    def data_dir(self):
        """Return data dir"""
        return self.config.data_dir
```

## 3. Use the Configuration

```python
# Initialize with default values
app = App()

# Initialize with custom configuration
custom_conf = {
    "config": {
        "root_dir": "/path/to/root",
        "module_dir": "/path/to/modules",
        "data_dir": "/path/to/data"
    }
}
app = App(value=custom_conf)

# Access configuration values
print(f"Root directory: {app.root_dir}")
print(f"Module directory: {app.module_dir}")
print(f"Data directory: {app.data_dir}")

# Get all configuration values
print(app.get_values())
```

## Key Features

- Declarative configuration definition
- Type checking and validation
- Environment variable support
- Nested configuration support
- Default values and help text
- Configuration inheritance
- Automatic CLI argument parsing

For more advanced usage and features, check out the [full documentation](../guides/guide_101/).

