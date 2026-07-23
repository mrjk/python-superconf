# Environment variables (12-factor)

Map environment variables onto nested config paths the same way Gitea/Forgejo do: `PREFIX__SECTION__KEY`. Use the helper `from_12factor` / `load_12factor` (not a method on `ConfigurationObj`) so apps stay 12-factor friendly without hand-wiring sources.

## Mapping rules

| Env var | Nested path |
|---|---|
| `APP__NAME=demo` | `{"name": "demo"}` |
| `APP__SERVER__HOST=0.0.0.0` | `{"server": {"host": "0.0.0.0"}}` |
| `APP__TAGS__0=api` | `{"tags": ["api"]}` |

- Prefix is required (case-insensitive); trailing `__` is optional.
- Path segments are separated by `__` and lowercased in the result.
- Digit-only segments become list indexes.
- Values stay strings until they are bound to a typed `ConfigurationObj`.

## Quick start

```python
from superconf import ConfigurationObj, FieldBool, FieldInt, FieldString, from_12factor

class AppConfig(ConfigurationObj):
    class Meta:
        env_prefix = "APP"

    name = FieldString(default="app")
    enabled = FieldBool(default=True)
    count = FieldInt(default=0)

# APP__ENABLED=false  APP__COUNT=42
config = from_12factor(AppConfig)
assert config.enabled is False
assert config.count == 42
```

`Meta.env_prefix` is a convention only: nothing reads the environment until you call `from_12factor` / `load_12factor`.

## Precedence

Default order (highest first): **cli → env → file → defaults** (`TWELVE_FACTOR_ORDER`).

| Layer | How it is provided |
|---|---|
| `cli` | `cli={...}` mapping (e.g. from argparse/`click`) |
| `env` | `PREFIX__PATH` via `env_prefix=` or `Meta.env_prefix` |
| `file` | `file="config.yml"` (also `.yaml`, `.json`, `.toml`) |
| `defaults` | Field defaults / `Meta.default` from an empty schema instance |

```python
config = from_12factor(
    AppConfig,
    file="config.yml",
    cli={"count": 25},  # wins over env and file
)
```

## CLI overrides

Pass a plain dict — convert flags yourself:

```python
import argparse
from superconf import from_12factor

parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int)
parser.add_argument("--name")
args = parser.parse_args()

cli = {key: value for key, value in vars(args).items() if value is not None}
config = from_12factor(AppConfig, cli=cli)
```

## Debugging layers

```python
from superconf import build_12factor_view

view = build_12factor_view(AppConfig, environ={"APP__NAME": "x"})
print(view.load_layers())
print(view.explain("name"))
print(view.materialize())
```

## Advanced: raw sources

For custom order or extra sources, use `EnvSource` + `View` directly (see [loading_from_files.md](loading_from_files.md) and `lab/test53_views.py`):

```python
from superconf import ConfigurationObj, EnvSource, FieldString, TWELVE_FACTOR_ORDER, View

class AppConfig(ConfigurationObj):
    name = FieldString(default="app")

view = View(order=TWELVE_FACTOR_ORDER)
view.add(EnvSource("env", prefix="APP"))
config = AppConfig(value=view.materialize())
```

## See also

- [Load from files](loading_from_files.md)
- Lab: `lab/test54_twelve_factor.py`
