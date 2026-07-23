---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Merge policies

This guide introduces combining two configuration instances with `merge()`, and
how to control that with `Meta.merge` and per-field `merge=`.

You should already know `ConfigurationObj`, fields, and `Meta` (guides 101–105).

## Why merge?

Typical need: start from defaults (or a base file), then apply an overlay
(environment, CLI, second file) without rewriting the whole tree by hand.

```python
from superconf import ConfigurationObj, FieldInt, FieldList, FieldString

class AppConfig(ConfigurationObj):
    name = FieldString(default="app")
    workers = FieldInt(default=2)
    tags = FieldList(default=[])

base = AppConfig(value={"name": "api", "tags": ["core"]})
overlay = AppConfig(value={"workers": 8, "tags": ["prod"]})
merged = base.merge(overlay)

print(merged.get_value())
# {'name': 'api', 'workers': 8, 'tags': ['core', 'prod']}
```

Notes:

* `merge()` returns a **new** object; `base` and `overlay` stay unchanged.
* Scalars use policy `override` by default (right wins when set).
* Lists (`FieldList`) use policy `append` by default.

## Declaring a policy on Meta

`Meta.merge` sets the policy for **this** container (how it combines with a peer
of the same kind):

```python
from superconf import MergeStrategy

class AppConfig(ConfigurationObj):
    class Meta:
        merge = MergeStrategy.OVERRIDE  # default for dict/obj; can omit

    name = FieldString(default="app")
```

Strings work the same: `merge = "override"`.

## Overriding per field

Field kwargs beat `Meta` (same precedence as `cast`):

```python
class AppConfig(ConfigurationObj):
    class Meta:
        merge = "override"

    # Stay frozen when parent deep-merges
    build_id = FieldInt(default=0, merge=MergeStrategy.KEEP)
    name = FieldString(default="app")
    tags = FieldList(default=[], merge="replace")  # old-style full replace
```

## Strategy cheat sheet

| Kind | Default | Allowed |
|------|---------|---------|
| Scalar | `override` | `override`, `override_non_null`, `keep` |
| Dict / Obj | `override` | `override`, `replace`, `override_present`, `override_absent`, `keep` |
| List | `append` | `append`, `prepend`, `replace`, `keep` |

Full tables and recipes: [merging_configurations.md](../howto/merging_configurations.md).

## Migration note (lists)

Before merge policies, a list field that was set on the right **replaced** the
left list. That behavior is `merge="replace"` now. The new default is `append`.

```python
# Explicit old behavior
tags = FieldList(default=[], merge="replace")
```

## Next steps

* How-to recipes: [merging_configurations.md](../howto/merging_configurations.md)
* Internals / copy: [merge_and_copy.md](../implementation/merge_and_copy.md)
* Previous guide: [105_meta_and_casting.md](105_meta_and_casting.md)
