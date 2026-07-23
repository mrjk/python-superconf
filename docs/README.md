# SuperConf documentation

Documentation follows the structure below.

## Guides

Learn the library step by step. Each guide introduces a small set of concepts.

| Guide | Topic |
|---|---|
| [101_simplest_structure.md](guides/101_simplest_structure.md) | `ConfigurationObj`, `Field`, access patterns |
| [102_fieldtypes_and_default_values.md](guides/102_fieldtypes_and_default_values.md) | Typed fields, `NOT_SET*` |
| [103_nested_structures.md](guides/103_nested_structures.md) | `FieldConf`, leaf vs container, dunders |
| [104_dynamic_fields.md](guides/104_dynamic_fields.md) | `ConfigurationDict` / `ConfigurationList`, short form |
| [105_meta_and_casting.md](guides/105_meta_and_casting.md) | `Meta`, casting, `children_class` |
| [106_merge_policies.md](guides/106_merge_policies.md) | `merge()`, `Meta.merge`, per-field policies |

## How-to

Practical recipes for common tasks.

| Topic | File |
|---|---|
| Load YAML / JSON | [howto/loading_from_files.md](howto/loading_from_files.md) |
| Environment variables (12-factor) | [howto/environment_variables.md](howto/environment_variables.md) |
| Short `FieldConf` syntax | [howto/short_syntax.md](howto/short_syntax.md) |
| Path anchors | [howto/path_anchors.md](howto/path_anchors.md) |
| Merge configurations | [howto/merging_configurations.md](howto/merging_configurations.md) |

## Implementation

Internal behavior for contributors and advanced users.

| Topic | File |
|---|---|
| Leafs vs containers | [implementation/leafs_vs_containers.md](implementation/leafs_vs_containers.md) |
| Casting | [implementation/casting.md](implementation/casting.md) |
| Merge and copy | [implementation/merge_and_copy.md](implementation/merge_and_copy.md) |

## Reference

API reference should be generated from code (not hand-written). See package exports in `superconf/__init__.py`.

## Project / maintainers

| Topic | File |
|---|---|
| Development setup (mise, `.venv`, Task) | [project/setup.md](project/setup.md) |
| Release (bump, tag, PyPI) | [project/release.md](project/release.md) |
