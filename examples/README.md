# Examples

Short, runnable demos of SuperConf. These are part of the test suite (`task test_examples`).

## Run

All examples:

```bash
task test_examples
# or: PYTHON=.venv/bin/python bash ./scripts/run_python_scripts.sh examples 'example[0-9]*'
```

Single file:

```bash
.venv/bin/python examples/example01_basics.py
```

## Index

| File | Topic |
|------|--------|
| `example01_basics.py` | `ConfigurationObj`, `Field`, access patterns, defaults |
| `example02_field_types.py` | Typed fields and `NOT_SET` sentinels |
| `example03_nested.py` | Nested objects with `FieldConf` |
| `example04_dynamic_dict.py` | `ConfigurationDict` + `children_class` |
| `example05_dynamic_list.py` | `ConfigurationList` + `children_class` |
| `example06_twelve_factor.py` | `from_12factor` / env + cli overlays |
| `example07_meta_extra_fields.py` | Meta defaults and `extra_fields` |
| `example08_shortform.py` | `FieldConf` shortform (`ConfigurationDict` + `children_class`) |
| `example09_merge.py` | Merge policies (obj, dict, list) |
| `example10_views.py` | Layered `View` with sources |
| `example11_anchors.py` | `PathAnchor` / `FileAnchor` |
