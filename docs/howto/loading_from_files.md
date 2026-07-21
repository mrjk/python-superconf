# Load configuration from YAML or JSON

Two approaches:

1. **Sources (recommended for files):** `YamlSource` / `JsonSource` / `TomlSource`
2. **Manual parse:** `from_yaml` / `from_json` (or stdlib), then pass a dict as `value=`

## Using sources

```python
from pathlib import Path

from superconf import ConfigurationObj, FieldBool, FieldConf, FieldInt, FieldString
from superconf import YamlSource, JsonSource, View

class ServerConfig(ConfigurationObj):
    host = FieldString(default="localhost")
    port = FieldInt(default=8080)

class AppConfig(ConfigurationObj):
    app_name = FieldString(default="app")
    debug = FieldBool(default=False)
    server = FieldConf(ServerConfig)

# Load a single file
file_src = YamlSource("file", path="config.yml")
config = AppConfig(value=file_src.load())

# Or materialize layered sources (file + env + defaults, etc.)
view = View(order=["file"])
view.add(file_src)
config = AppConfig(value=view.materialize())
```

`JsonSource` and `TomlSource` work the same way (`path=` or inline `data=`).

## Helpers (manual parse)

```python
from pathlib import Path
from superconf.common import from_yaml, from_json, to_yaml, to_json
```

- `from_yaml(string)` / `from_json(string)` → Python object
- `to_yaml(obj)` / `to_json(obj)` → string (useful with `config.get_value()`)

You can also use `yaml.safe_load` / `json.loads` directly.

## Example

`config.yml`:

```yaml
app_name: demo
debug: true
server:
  host: 0.0.0.0
  port: 9000
```

```python
from pathlib import Path

from superconf import ConfigurationObj, FieldBool, FieldConf, FieldInt, FieldString
from superconf.common import from_yaml

class ServerConfig(ConfigurationObj):
    host = FieldString(default="localhost")
    port = FieldInt(default=8080)

class AppConfig(ConfigurationObj):
    app_name = FieldString(default="app")
    debug = FieldBool(default=False)
    server = FieldConf(ServerConfig)

raw = from_yaml(Path("config.yml").read_text(encoding="utf-8"))
config = AppConfig(value=raw)

assert config.app_name == "demo"
assert config.debug is True
assert config.server.port == 9000
```

## JSON

```python
from pathlib import Path
import json

from superconf.common import from_json

raw = from_json(Path("config.json").read_text(encoding="utf-8"))
# or: raw = json.loads(Path("config.json").read_text(encoding="utf-8"))
config = AppConfig(value=raw)
```

## Dump back

```python
from superconf.common import to_yaml, to_json

print(to_yaml(config.get_value()))
print(to_json(config.get_value()))
```
