"""Typed fields and NOT_SET / NOT_SET_DICT / NOT_SET_LIST sentinels."""

from pprint import pprint

from superconf import (
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    ConfigurationObj,
    Field,
    FieldBool,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldList,
    FieldString,
    FieldTuple,
)


class AppConfig(ConfigurationObj):
    """Configuration with various field types."""

    is_enabled = FieldBool(default=True)
    debug_mode = FieldBool(default="yes")  # cast to True
    verbose_logs = FieldBool(default="off")  # cast to False

    app_name = FieldString(default="MyApp")
    version = FieldString(default="1.0.0")

    worker_count = FieldInt(default=4)
    timeout = FieldFloat(default=5.5)

    tags = FieldList(default=["web", "api"])
    settings = FieldDict(default={"theme": "dark"})
    dimensions = FieldTuple(default=(800, 600))

    unset = Field()
    unset_string = FieldString()
    unset_dict = FieldDict()
    unset_list = FieldList()


app = AppConfig()

print("Typed defaults:")
pprint(app.get_value())

assert app.is_enabled is True
assert app.debug_mode is True
assert app.verbose_logs is False
assert app.worker_count == 4
assert app.timeout == 5.5
assert app.tags == ["web", "api"]
assert app.settings == {"theme": "dark"}
assert app.dimensions == (800, 600)

print("\nUnset sentinels:")
print(f"  unset is NOT_SET: {app.unset is NOT_SET}")
print(f"  unset_string (FieldString casts sentinel): {app.unset_string!r}")
print(f"  unset_dict == NOT_SET_DICT: {app.unset_dict == NOT_SET_DICT}")
print(f"  unset_list == NOT_SET_LIST: {app.unset_list == NOT_SET_LIST}")

assert app.unset is NOT_SET
# FieldString casts the sentinel to a string representation
assert app.unset_string == "<NOT_SET>"
assert app.unset_dict == NOT_SET_DICT
assert app.unset_list == NOT_SET_LIST

# Assign a previously unset field
app.unset_string = "now set"
assert app.unset_string == "now set"
print(f"\nAfter assign: unset_string={app.unset_string!r}")

print("\nOK")
