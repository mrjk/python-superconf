# Merge and copy

Containers and leaves support combining and duplicating trees.

## `merge(other)`

`obj.merge(other)` returns a **new** instance of the same type. Inputs are not
mutated. Non-`Leaf` `other` raises `ValueError`.

Policy resolution (left node governs each step):

1. `Field(..., merge=...)` / `FieldConf(..., merge=...)`
2. `class Meta: merge = ...`
3. Type default on `__node_config__` / Field class attr

Nested children keep their own resolved `__node_merge__` when the parent
deep-merges.

### API surface

| Symbol | Role |
|--------|------|
| `MergeStrategy` | `str` enum (`OVERRIDE`, `APPEND`, …) |
| `MERGE_*` aliases | Same members (`MERGE_OVERRIDE`, …) |
| `MergeKind` | `OTHER` / `DICT` / `LIST` |
| `normalize_merge_strategy` | Enum or string → `MergeStrategy` |
| `merge_data` | Merge plain list/dict values |
| `merge_maps` | Merge keyed maps with `merge_both` callback |
| `prefer_other_scalar` | Scalar left/right choice |

Implementation module: [`superconf/merge.py`](../../superconf/merge.py)
(re-exported from `superconf.common` / package root for common symbols).

### Strategies by kind

**Other (scalars)** — default `override`:

| Strategy | Behavior |
|----------|----------|
| `override` | Take other when set; else keep self |
| `override_non_null` | Take other when set and not `None`; else keep self |
| `keep` | Prefer self when set; else take other |

**Dict** (`ConfigurationDict` / `ConfigurationObj` / `FieldDict`) — default `override`:

| Strategy | Behavior |
|----------|----------|
| `override` | Deep-merge: union of keys; shared keys recurse |
| `replace` | Take other whole |
| `override_present` | Only update keys already in self; ignore keys only in other |
| `override_absent` | Only add keys missing from self; do not overwrite existing |
| `keep` | Keep self whole |

**List** (`ConfigurationList` / `FieldList`) — default `append`:

| Strategy | Behavior |
|----------|----------|
| `replace` | Take other whole |
| `prepend` | other + self |
| `append` | self + other |
| `keep` | Keep self whole |

Invalid strategy for a kind raises `ValueError`.

### Call flow

```text
a.merge(b)
  └─ read a.__node_merge__
       ├─ LIST / DICT leaf values → merge_data(...)
       ├─ OTHER leaf             → prefer_other_scalar(...) → a or b
       ├─ ConfigurationDict/Obj  → merge_maps(children, merge_both=child.merge)
       └─ ConfigurationList      → merge_data(..., kind=LIST)
```

### Example

```python
from superconf import ConfigurationObj, FieldBool, FieldInt, FieldList, FieldString
from superconf import MergeStrategy

class AppConfig(ConfigurationObj):
    class Meta:
        merge = MergeStrategy.OVERRIDE  # dict default; can omit

    name = FieldString(default="default")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999, merge=MergeStrategy.KEEP)
    tags = FieldList(default=[])  # list default: append

left = AppConfig(value={"name": "toto", "count": 25, "tags": ["a"]})
right = AppConfig(value={"name": "titi", "enabled": False, "count": 1, "tags": ["b"]})
merged = left.merge(right)

assert merged.get_value() == {
    "name": "titi",
    "enabled": False,
    "count": 25,
    "tags": ["a", "b"],
}
```

### Migration: list default

Before merge policies, `Leaf.merge` replaced a list when the right side was set
(today’s `replace`). Default is now `append`. Opt into the old behavior with
`FieldList(..., merge="replace")` or `Meta.merge = "replace"` on a list container.

## `copy()` / `deepcopy()`

- `copy()` — shallow copy of the node
- `deepcopy()` — recursively copies children

Use these when you need an independent tree without mutating the original.

## Related

- How-to: [merging_configurations.md](../howto/merging_configurations.md)
- Guide: [106_merge_policies.md](../guides/106_merge_policies.md)
- Source: `Leaf.merge`, `ConfigurationDict.merge`, `ConfigurationList.merge`
- Tests: `tests/test_42_parametrized_merge.py`
- Lab: `lab/test51_merges.py`
