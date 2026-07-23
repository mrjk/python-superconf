# Leafs vs containers

SuperConf nodes form a tree.

## Leaf

A **leaf** stores one value. Runtime class: `Leaf` (usually created via `Field` / typed fields).

- No children
- `get_value()` returns the casted value
- Attribute / `[]` access on the parent returns that value

## Containers

A **container** holds named or indexed children.

| Class | Shape | Typical use |
|---|---|---|
| `ConfigurationObj` | fixed declared fields (+ optional extras) | Application schema |
| `ConfigurationDict` | dynamic string keys | Maps / registries |
| `ConfigurationList` | dynamic integer indexes | Ordered collections |

Containers are also `Leaf` subclasses in the hierarchy, but they manage children instead of a single scalar payload.

## Access semantics

On a container `obj`:

| Call | Result |
|---|---|
| `obj.child` | leaf → value; container → child node |
| `obj["child"]` | always value |
| `obj("child")` | always child node |

## Nesting

`FieldConf(ChildClass)` embeds another container (or leaf class) as a declared child of a `ConfigurationObj`.

Variadic containers use `Meta.children_class` (or short-form `FieldConf(ConfigurationDict, children_class=...)`).

## Related

- Guides [103](../guides/103_nested_structures.md) and [104](../guides/104_dynamic_fields.md)
- Source: `superconf/leaf.py`, `superconf/container.py`
  (`superconf/configuration.py` re-exports for compatibility)
