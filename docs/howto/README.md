# ⚡ Superconf How-To Guides

<div align="center">
  <h3>Practical solutions for common Superconf tasks</h3>
</div>

---

## 📚 Available How-To Guides

These guides focus on solving specific problems with Superconf:

| Guide | Description |
|-------|-------------|
| [Loading from Files](01_loading_from_files.md) | How to load configuration from YAML, JSON, and other file formats |
| [Environment Variables](02_environment_variables.md) | How to configure your application using environment variables |
| [Custom Field Types](03_custom_field_types.md) | How to create specialized field types with validation and transformation |
| [Configuration Inheritance](04_config_inheritance.md) | How to create reusable configuration hierarchies |

## 🎯 Problem-Oriented Guides

Each guide is designed to solve a specific problem. Choose the guide that matches your current need:

### I need to...

- **Load config from files** → [Loading from Files](01_loading_from_files.md)
- **Use environment variables** → [Environment Variables](02_environment_variables.md)
- **Create custom field types** → [Custom Field Types](03_custom_field_types.md)
- **Build a config hierarchy** → [Configuration Inheritance](04_config_inheritance.md)

## 🚀 Quick Solutions

Need a quick solution? Here are some common tasks:

```python
# Loading from YAML file
import yaml
from superconf.configuration import ContainerConf
from superconf.fields import FieldString, FieldInt

class AppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    port = FieldInt(default=8000)

# Load config
with open("config.yml", "r") as file:
    config_data = yaml.safe_load(file)
config = AppConfig(**config_data)
```

## 📋 Prerequisites

These guides assume you:

- Have a basic understanding of Superconf
- Have Superconf installed in your environment
- Are familiar with Python programming

If you're new to Superconf, start with the [Tutorials](../tutorials/README.md) first.

## 🔄 Navigation

- [📚 Main Documentation](../README.md)
- [🧠 Tutorials](../tutorials/README.md)
- [🔍 Implementation Details](../implementation/README.md)

## When to Use How-To Guides

These guides are most useful when:

- You know what you want to accomplish but not how to do it
- You need a practical solution to a specific problem
- You want to see real-world examples of Superconf in action
- You're extending Superconf for your specific needs

## Related Documentation

For a more conceptual understanding, see:

- [Tutorials](../tutorials/README.md) - Step-by-step guides for beginners
- [Explanations](../explanation/README.md) - In-depth discussions about how Superconf works
- [API Reference](../reference/README.md) - Complete class and function documentation 