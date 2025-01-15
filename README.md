# SuperConf

A powerful and flexible configuration management library for Python, inspired by [ClassyConf](https://classyconf.readthedocs.io/en/latest/). SuperConf provides a clean, type-safe, and intuitive way to handle configuration from multiple sources including environment variables, configuration files, and dictionaries.

Inspired from cafram and [Cafram](https://classyconf.readthedocs.io/en/latest/)

## Features

- 🔒 Type-safe configuration with built-in validation
- 🔄 Multiple configuration sources (environment variables, files, dictionaries)
- 📦 Nested configuration support
- 🎯 Default values and custom casting
- 🚀 Easy to use and extend
- 🔍 Strict type checking mode
- 📝 Comprehensive field types (Boolean, Integer, String, List, Dict, etc.)
- 🎨 Support for custom field types

## Quickstart

### Installation

Install using pip:
```bash
pip install superconf
```

Or install from source:
```bash
git clone https://github.com/mrjk/python-superconf2.git
cd python-superconf2
pip install -e .
```

### Basic Usage

Here's a simple example of how to use SuperConf:

```python
from superconf.configuration import Configuration
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList

class AppConfig(Configuration):
    class Meta:
        loaders = [Environment()]  # Load from environment variables
    
    debug = FieldBool(default=False, help="Enable debug mode")
    port = FieldInt(default=8080, help="Server port")
    app_name = FieldString(default="myapp", help="Application name")
    plugins = FieldList(default=[], help="Enabled plugins")

# Create and use the configuration
config = AppConfig()
print(config.debug)  # False
print(config.port)   # 8080

# Use environment variables to override defaults
# export APP_PORT=9000
# export APP_DEBUG=true
```

## Overview

### Requirements

- Python 3.9 or higher
- Dependencies:
  - pyaml >= 24.12.1
  - classyconf >= 0.5.2

### FAQ

**Q: How is SuperConf different from other configuration libraries?**  
A: SuperConf combines the best features of existing libraries with strong type safety, nested configurations, and a clean API.

**Q: Can I use multiple configuration sources?**  
A: Yes, SuperConf supports multiple loaders that can be prioritized in order.

**Q: Is it possible to extend SuperConf with custom field types?**  
A: Yes, you can create custom field types by extending the `Field` class.

### Known Issues

- String parsing for dictionary fields is not implemented yet
- Cache settings need refinement
- Some features are marked as WIP (Work in Progress)

## Development

### Setup Development Environment

1. Clone the repository:
```bash
git clone https://github.com/mrjk/python-superconf2.git
cd python-superconf2
```

2. Install development dependencies:
```bash
poetry install
```

### Development Commands

SuperConf uses [Taskfile](https://taskfile.dev) for development tasks:

- Run tests: `task test`
- Run linting: `task test_lint`
- Fix linting issues: `task fix_lint`
- Generate documentation: `task gen_doc_class_graph`

### Running Tests

```bash
task test        # Run all tests
task test_pytest # Run pytest suite
task test_recap  # View test coverage report
```

## Project Information

### License

This project is licensed under the GPLv3 License.

### Author

- mrjk <mrjk.78@gmail.com>

### Support

For support, please:
1. Check the [documentation](https://github.com/mrjk/python-superconf2/docs)
2. Open an issue on [GitHub](https://github.com/mrjk/python-superconf2/issues)

### Related Projects

- [ClassyConf](https://classyconf.readthedocs.io/en/latest/)
- [python-decouple](https://github.com/henriquebastos/python-decouple)
- [dynaconf](https://www.dynaconf.com/)

### Roadmap

- [ ] Implement string parsing for dictionary fields
- [ ] Improve caching mechanism
- [ ] Add more configuration sources
- [ ] Create comprehensive documentation site
- [ ] Add more examples and use cases
- [ ] Implement configuration validation hooks
