# Casting

Casting converts raw input into the type expected by a field or container.

## Where it runs

Values are cast when defaults and overrides are applied (`node_cast_value` in `configuration.py`), typically during construction and `set_value`.

## Built-in field casts

| Field | Default cast |
|---|---|
| `FieldBool` | `as_boolean` |
| `FieldString` | `str` (via string cast) |
| `FieldInt` | `as_int` |
| `FieldFloat` | `float` |
| `FieldList` | `as_list` |
| `FieldTuple` | `as_tuple` |
| `FieldDict` | `as_dict` |
| `Field` | identity (`as_is` / none) |

Helpers live in `superconf.casts` and are re-exported from `superconf` (`as_boolean`, `as_int`, `as_list`, `as_dict`, `as_tuple`, `as_is`).

## Custom casts

Pass any callable (or `AbstractCast` subclass) as `cast=` on a field:

```python
Field(default="admin", cast=my_callable)
```

Container-level `Meta.cast` must match the container payload type (dict/list). An incompatible cast raises `InvalidCastConfiguration`.

## Sentinels and casting

Unset typed fields still go through their cast. Example: `FieldString()` surfaces as the string `"<NOT_SET>"` rather than the `NOT_SET` sentinel. Untyped `Field()` keeps `NOT_SET`. Dict/list fields use `NOT_SET_DICT` / `NOT_SET_LIST`.

## Related

- Guide [105](../guides/105_meta_and_casting.md)
- Source: `superconf/casts.py`, `superconf/fields.py`
