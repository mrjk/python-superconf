# Merge and copy

Containers and leaves support combining and duplicating trees.

## `merge(other)`

`obj.merge(other)` returns a **new** instance of the same type:

- Leaf: prefers `other` when it has a value; otherwise keeps `self`
- Dict / Obj: deep-merges matching children; keys only in `other` are added

```python
from superconf import ConfigurationObj, FieldBool, FieldInt, FieldString

class AppConfig(ConfigurationObj):
    name = FieldString(default="default")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)

left = AppConfig(value={"name": "toto", "count": 25})
right = AppConfig(value={"name": "titi", "enabled": False})
merged = left.merge(right)

assert merged.get_value() == {"name": "titi", "enabled": False, "count": 25}
```

Works the same for `ConfigurationDict` of nested objects (see `lab/test51_merges.py`).

## `copy()` / `deepcopy()`

- `copy()` — shallow copy of the node
- `deepcopy()` — recursively copies children

Use these when you need an independent tree without mutating the original.

## Related

- Source: `Leaf.merge`, `ConfigurationDict.merge` in `superconf/configuration.py`
- Lab: `lab/test51_merges.py`
