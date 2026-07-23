"""Merge ConfigurationObj / ConfigurationDict trees and list strategies."""

from pprint import pprint

from superconf import (
    MERGE_APPEND,
    MERGE_KEEP,
    MERGE_REPLACE,
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
    FieldBool,
    FieldInt,
    FieldList,
    FieldString,
)


class AppConfig(ConfigurationObj):
    """Simple app settings."""

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


class AppDict(ConfigurationDict):
    """Map of AppConfig children."""

    class Meta:
        children_class = AppConfig


# Merge two ConfigurationObj instances (right overrides present keys)
left = AppConfig(value={"name": "toto", "count": 25})
right = AppConfig(value={"name": "titi", "enabled": False})
merged = left.merge(right)
print("Obj merge:")
pprint(merged.get_value())
assert merged.get_value() == {"count": 25, "enabled": False, "name": "titi"}


# Merge ConfigurationDict maps (deep merge per child)
dict_left = AppDict(
    value={
        "app1": {"name": "toto", "count": 64},
        "app2": {"name": "titi", "enabled": False},
    }
)
dict_right = AppDict(
    value={
        "app1": {"name": "tata"},
        "app3": {"name": "tutu", "enabled": True},
    }
)
dict_merged = dict_left.merge(dict_right)
print("\nDict merge:")
pprint(dict_merged.get_value())
assert dict_merged.app1.name == "tata"
assert dict_merged.app1.count == 64
assert "app3" in dict_merged.get_value()


# Meta.merge = REPLACE / KEEP
class CfgReplace(ConfigurationObj):
    """Right side fully replaces left."""

    class Meta:
        merge = MERGE_REPLACE

    name = FieldString(default="left")
    count = FieldInt(default=1)


class CfgKeep(ConfigurationObj):
    """Left side wins (keep)."""

    class Meta:
        merge = MERGE_KEEP

    name = FieldString(default="left")
    count = FieldInt(default=1)


assert CfgReplace(value={"name": "a", "count": 10}).merge(
    CfgReplace(value={"name": "b"})
).get_value() == {"name": "b", "count": 1}

assert CfgKeep(value={"name": "a", "count": 10}).merge(
    CfgKeep(value={"name": "b"})
).get_value() == {"name": "a", "count": 10}
print("\nREPLACE and KEEP strategies OK")


# List merge: default append
class TagList(ConfigurationList):
    """List of strings with append merge."""

    class Meta:
        merge = MERGE_APPEND
        children_class = FieldString


class WithTags(ConfigurationObj):
    """Config with a mergeable tag list."""

    tags = FieldList(default=["a"], merge=MERGE_APPEND)


base = WithTags(value={"tags": ["a", "b"]})
overlay = WithTags(value={"tags": ["c"]})
print("\nList append merge:")
pprint(base.merge(overlay).get_value())
assert base.merge(overlay).tags == ["a", "b", "c"]

print("\nOK")
