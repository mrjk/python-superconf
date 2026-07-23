"""PathAnchor and FileAnchor for relative / absolute path resolution."""

from pprint import pprint

from superconf import FileAnchor, PathAnchor


project = PathAnchor("/fake/prj")
inventory = PathAnchor("inventory/", parent=project)
config_dir = PathAnchor("../../common_conf", parent=project)

print("Roots:")
print(f"  project:   {project.get_dir(clean=True)}")
print(f"  inventory: {inventory.get_dir(clean=True)}")
print(f"  config:    {config_dir.get_dir(clean=True)}")

assert project.get_dir(clean=True) == "/fake/prj"
assert inventory.get_dir(clean=True) == "/fake/prj/inventory"

# Relative child under inventory
rel = PathAnchor("subdir/file.yml", parent=inventory)
print(f"\nRelative child: {rel.get_dir(clean=True)}")
assert rel.get_dir(clean=True) == "/fake/prj/inventory/subdir/file.yml"

# Absolute child ignores parent for the absolute segment
abs_child = PathAnchor("/etc/app/config.yml", parent=project)
print(f"Absolute child: {abs_child.get_dir(clean=True)}")
assert abs_child.get_dir(clean=True).startswith("/")

# FileAnchor tracks file + directory
file_anchor = FileAnchor("subconf/myfile.yml", parent=project)
info = {
    "path": file_anchor.get_path(clean=True),
    "dir": file_anchor.get_dir(clean=True),
    "name": file_anchor.get_name(),
}
print("\nFileAnchor:")
pprint(info)
assert info["name"] == "myfile.yml"
assert info["path"].endswith("subconf/myfile.yml")

print("\nOK")
