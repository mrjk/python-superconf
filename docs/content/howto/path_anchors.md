# Path anchors

`PathAnchor` and `FileAnchor` resolve filesystem paths relative to a parent anchor. Exported from `superconf` as `PathAnchor`, `FileAnchor`, `ABS` / `ABSOLUTE`, `REL` / `RELATIVE`.

## Basics

```python
from superconf import PathAnchor, FileAnchor, ABS, REL

project = PathAnchor("/fake/prj")
conf = PathAnchor("../../common_conf", parent=project, mode=ABS)
inventory = PathAnchor("inventory/", parent=conf, mode=REL)

print(conf.get_dir())       # absolute when mode=ABS
print(inventory.get_dir())  # relative when mode=REL
print(inventory.get_path()) # same family of helpers
```

`mode` is `"abs"` / `"rel"` (aliases `ABS`/`ABSOLUTE`, `REL`/`RELATIVE`). Pass `clean=True` to normalize `.` / `..` components.

## Files

```python
root = PathAnchor("/fake/prj")
config_file = FileAnchor("subconf/myfile.yml", parent=root)

config_file.get_path()  # /fake/prj/subconf/myfile.yml
config_file.get_file()  # myfile.yml
config_file.get_dir()   # /fake/prj/subconf
```

## When to use

Keep a project root as an absolute anchor, then hang relative config/data paths under it so resolution stays stable when the process cwd changes.

Runnable examples: `examples/example11_anchors.py`.
