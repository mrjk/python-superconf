# SuperConf

<!--- pyml disable-num-lines 20 no-inline-html -->
<p align='center'>
<a href="https://github.com/mrjk/python-superconf">
<img src="logo/banner.svg" alt="SuperConf Logo"></a>
</p>

<p align="center">
<a href="https://github.com/mrjk/python-superconf">
<img src="https://img.shields.io/badge/github-%23121011.svg?style=Flat&logo=github&logoColor=blue&label=Repo" alt="Github Repo"></a>
<a href="https://mrjk.github.io/python-superconf/">
<img src="https://img.shields.io/badge/github%20pages-121013?style=Flat&logo=github&logoColor=blue&label=Page" alt="Github Page"></a>
<a href="https://github.com/mrjk/python-superconf/tags/">
<img src="https://img.shields.io/badge/github-%23121011.svg?style=Flat&logo=github&logoColor=blue&label=Releases" alt="Github Releases"></a>
</p>

<p align="center">
<img src="https://img.shields.io/pypi/pyversions/superconf" alt="PyPI - Python Version">
<img src="https://img.shields.io/pypi/format/superconf" alt="PyPI - Format">
<img src="https://img.shields.io/pypi/status/superconf" alt="PyPI - Status">
</p>

<p align="center">
<a href="https://gitter.im/mrjk/python-superconf">
<img src="https://img.shields.io/gitter/room/mrjk/python-superconf" alt="Gitter"></a>
<a href="https://pypi.org/project/superconf/">
<img src="https://img.shields.io/pypi/v/superconf" alt="PyPI"></a>
<a href="https://pypistats.org/packages/superconf">
<img src="https://img.shields.io/pypi/dm/superconf" alt="PyPI - Downloads"></a>
<a href="https://github.com/mrjk/python-superconf/releases">
<img src="https://img.shields.io/piwheels/v/superconf?include_prereleases" alt="piwheels (including prereleases)"></a>
<a href="https://github.com/mrjk/python-superconf/graphs/code-frequency">
<img src="https://img.shields.io/github/commit-activity/m/mrjk/python-superconf" alt="GitHub commit activity"></a>
<a href="https://www.gnu.org/licenses/gpl-3.0">
<img src="https://img.shields.io/badge/License-GPL%20v3-blue.svg" alt="License: GPL v3"></a>
</p>

-------

This project is in Beta.

SuperConf is a Python library for structured configuration: declare a model with typed fields and nested containers, then load values from dicts, files (`YamlSource` / `JsonSource` / `TomlSource`), environment (`EnvSource`), or layered `View`s.

Inspired by [Cafram](https://github.com/barbu-it/cafram), forked from [ClassyConf](https://classyconf.readthedocs.io/en/latest/).

## Features

- Type-aware fields (`FieldBool`, `FieldInt`, `FieldString`, `FieldList`, `FieldDict`, …)
- Nested models with `FieldConf`
- Dynamic dict/list containers (`ConfigurationDict`, `ConfigurationList`)
- Defaults, custom casting, and `Meta` options (`extra_fields`, `default`, `children_class`, …)
- Clear access rules: attribute / `[]` / call (`obj("key")`)
- File / env / dict sources and multi-source `View` precedence
- Merge policies (`merge()`, `MergeStrategy`)
- Path helpers (`PathAnchor`, `FileAnchor`)

## Quickstart

### Installation

```bash
pip install superconf
```

Or from source:

```bash
git clone https://github.com/mrjk/python-superconf.git
cd python-superconf
poetry install
```

### Basic usage

```python
from superconf import ConfigurationObj, FieldBool, FieldInt, FieldString, FieldList

class AppConfig(ConfigurationObj):
    debug = FieldBool(default=False, help="Enable debug mode")
    port = FieldInt(default=8080, help="Server port")
    app_name = FieldString(default="myapp", help="Application name")
    plugins = FieldList(default=[], help="Enabled plugins")

# Defaults
config = AppConfig()
assert config.debug is False
assert config.port == 8080

# Override from a dict (e.g. parsed YAML/JSON)
config = AppConfig(value={
    "debug": "yes",
    "port": "9000",
    "plugins": ["auth", "cache"],
})
assert config.debug is True
assert config.port == 9000
assert config.plugins == ["auth", "cache"]

# Dump as plain data
print(config.get_value())
```

### Nested configuration

```python
from superconf import ConfigurationObj, FieldConf, FieldInt, FieldString

class ServerConfig(ConfigurationObj):
    host = FieldString(default="localhost")
    port = FieldInt(default=8080)

class AppConfig(ConfigurationObj):
    name = FieldString(default="myapp")
    server = FieldConf(ServerConfig)

app = AppConfig(value={"server": {"port": 9000}})
assert app.server.host == "localhost"
assert app.server.port == 9000
```

## Documentation

| Section | Path |
|---|---|
| Guides (start here) | [docs/guides/](docs/guides/) |
| How-to | [docs/howto/](docs/howto/) |
| Implementation notes | [docs/implementation/](docs/implementation/) |

Suggested reading order:

1. [101 — Simplest structure](docs/guides/101_simplest_structure.md)
2. [102 — Field types and unset values](docs/guides/102_fieldtypes_and_default_values.md)
3. [103 — Nested structures](docs/guides/103_nested_structures.md)
4. [104 — Dynamic dict/list fields](docs/guides/104_dynamic_fields.md)
5. [105 — Meta and casting](docs/guides/105_meta_and_casting.md)
6. [106 — Merge policies](docs/guides/106_merge_policies.md)

## Overview

### Requirements

- Python 3.9+
- Runtime dependencies: `pyaml`, `sentinel`

### Access cheat sheet

| Access | Leaf field | Container field |
|---|---|---|
| `obj.key` | value | container node |
| `obj["key"]` | value | value (dict/list) |
| `obj("key")` / `obj.get_child("key")` | node (`Leaf`) | node |

### FAQ

**How do I load YAML or JSON?**  
Use `YamlSource` / `JsonSource` / `TomlSource` (see `superconf.sources`), or parse yourself (`yaml.safe_load`, `from_yaml`, …) and pass `value=`. See [Load from files](docs/howto/loading_from_files.md).

**Are environment loaders built in?**  
Yes, as helpers: ``from_12factor(AppConfig, file="config.yml", cli={...})``
(or ``Meta.env_prefix``). Mapping is Gitea-style ``PREFIX__PATH``.
Precedence: ``cli → env → file → defaults`` (``TWELVE_FACTOR_ORDER``).
See [Environment variables](docs/howto/environment_variables.md).
Lower-level: ``EnvSource`` + ``View``.

**Can I allow undeclared keys?**  
Yes, set `Meta.extra_fields = True` on a `ConfigurationObj`. Extra keys must be provided via `value=` / full `set_value({...})`, not by assigning a new attribute after init.

### Known limitations

- `FieldOption` is not available
- TOML dump needs optional ``tomli-w``; TOML load needs Python 3.11+ or ``tomli``

## Development

### Setup

```bash
git clone https://github.com/mrjk/python-superconf.git
cd python-superconf
poetry install
```

### Commands

Uses [Taskfile](https://taskfile.dev):

| Command | Purpose |
|---|---|
| `task test` | Lab + report + lint |
| `task test_pytest` | Pytest suite |
| `task test_lab` | Run lab scripts |
| `task test_lint` | Lint checks |
| `task fix_lint` | Auto-format with black/isort |

## Project information

### License

GPLv3

### Author

- mrjk <mrjk.78@gmail.com>

### Support

1. Read the [docs](docs/)
2. Open an issue on [GitHub](https://github.com/mrjk/python-superconf/issues)

### Related projects

- [ClassyConf](https://classyconf.readthedocs.io/en/latest/)
- [python-decouple](https://github.com/henriquebastos/python-decouple)
- [dynaconf](https://www.dynaconf.com/)
