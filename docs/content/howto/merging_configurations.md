# Merging configurations

Combine two configuration trees with `left.merge(right)`. The result is a **new**
instance; inputs are not mutated.

Merge behavior is controlled per node with the `merge` setting on `Meta` and/or
on each `Field`.

## Quick start

```python
from superconf import ConfigurationObj, FieldInt, FieldList, FieldString, MergeStrategy

class AppConfig(ConfigurationObj):
    name = FieldString(default="app")
    count = FieldInt(default=0)
    tags = FieldList(default=[])  # default list policy: append

base = AppConfig(value={"name": "api", "count": 2, "tags": ["a"]})
overlay = AppConfig(value={"name": "api-v2", "tags": ["b"]})
merged = base.merge(overlay)

assert merged.get_value() == {
    "name": "api-v2",   # scalar: override (right wins when set)
    "count": 2,         # kept from base (unset on overlay)
    "tags": ["a", "b"], # list: append
}
```

## Setting the policy

Precedence (same pattern as `cast`):

1. Field kwarg: `FieldInt(..., merge=...)`
2. Class `Meta.merge`
3. Type default (`override` for dict/scalar, `append` for lists)

Left side wins for policy choice: `a.merge(b)` uses **`a`'s** policy at each node.
Children use their own resolved policy when the parent deep-merges.

Use either the enum or a string:

```python
from superconf import MergeStrategy

class AppConfig(ConfigurationObj):
    class Meta:
        merge = MergeStrategy.OVERRIDE  # or "override"

    locked = FieldInt(default=1, merge=MergeStrategy.KEEP)  # or merge="keep"
    tags = FieldList(default=[], merge="replace")           # opt out of append
```

## Strategies by kind

### Scalars (other) — default `override`

| Strategy | Behavior |
|----------|----------|
| `override` | Take right when set; else keep left |
| `override_non_null` | Take right when set and not `None` |
| `keep` | Prefer left when set; else take right |

### Dict / `ConfigurationObj` / `FieldDict` — default `override`

| Strategy | Behavior |
|----------|----------|
| `override` | Deep-merge keys; shared keys recurse |
| `replace` | Take right tree whole |
| `override_present` | Only update keys already on left |
| `override_absent` | Only add keys missing on left |
| `keep` | Keep left tree whole |

### List / `ConfigurationList` / `FieldList` — default `append`

| Strategy | Behavior |
|----------|----------|
| `append` | left + right |
| `prepend` | right + left |
| `replace` | Take right list whole |
| `keep` | Keep left list whole |

## Common recipes

### Overlay defaults with an environment-specific config

```python
defaults = AppConfig(value={"name": "app", "tags": ["base"]})
prod = AppConfig(value={"name": "app-prod", "tags": ["prod"]})
runtime = defaults.merge(prod)
# tags -> ["base", "prod"] with FieldList default append
```

### Keep a field frozen while merging the rest

```python
class AppConfig(ConfigurationObj):
    version = FieldInt(default=1, merge=MergeStrategy.KEEP)
    name = FieldString(default="app")

left = AppConfig(value={"version": 3, "name": "a"})
right = AppConfig(value={"version": 99, "name": "b"})
assert left.merge(right).get_value() == {"version": 3, "name": "b"}
```

### Restore pre-policy list behavior (replace)

Before merge policies existed, a set list on the right **replaced** the left list.
That is `replace` today:

```python
class AppConfig(ConfigurationObj):
    tags = FieldList(default=[], merge=MergeStrategy.REPLACE)
```

### Nested dict of objects

```python
from superconf import ConfigurationDict

class Service(ConfigurationObj):
    host = FieldString(default="localhost")
    port = FieldInt(default=8080)

class Services(ConfigurationDict):
    class Meta:
        children_class = Service

left = Services(value={"api": {"port": 80}})
right = Services(value={"api": {"host": "api.local"}, "db": {"port": 5432}})
merged = left.merge(right)
# api deep-merged; db added
```

## See also

- Guide: [106_merge_policies.md](../guides/106_merge_policies.md)
- Implementation: [merge_and_copy.md](../implementation/merge_and_copy.md)
- Tests: `tests/test_42_parametrized_merge.py`
- Example: `examples/example09_merge.py`
