"""Declare a ConfigurationObj, access fields, and override defaults."""

from pprint import pprint

from superconf import ConfigurationObj, Field, Leaf, UndeclaredField, UnknownChild

CONFIG_BASE = {
    "item1": True,
    "item2": 4333,
}

CONFIG_OVERRIDE = {
    "item1": "yeah",
    "item2": 777,
}


class AppConfig(ConfigurationObj):
    """Simple model with defaults and help messages."""

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="A string field")
    field3 = Field(default=42, help="A numeric field")
    field4 = Field(default=CONFIG_BASE, help="A dictionary field")


# Defaults only
app = AppConfig()
assert app.field1 is False
assert app["field2"] == "Default value"
assert app.get_value("field3") == 42
assert isinstance(app("field1"), Leaf)
assert app("field1").get_value() is False
assert app.field4 == CONFIG_BASE

print("Defaults:")
pprint(app.get_value())

# Override via constructor
app = AppConfig(
    value={
        "field1": True,
        "field2": "Custom value",
        "field3": 51,
        "field4": CONFIG_OVERRIDE,
    }
)
assert app.field1 is True
assert app.field2 == "Custom value"
assert app("field3").get_default() == 42

print("\nWith overrides:")
pprint(app.get_value())

# Update values
app.set_value({"field2": "updated", "field3": 100})
app("field3").set_value(4242)
assert app.field3 == 4242

print("\nAfter set_value:")
pprint(app.get_value())

# Unknown fields
try:
    _ = app.get_value("field9")
except UndeclaredField:
    pass
else:
    raise AssertionError("expected UndeclaredField")

try:
    _ = app("field9")
except UnknownChild:
    pass
else:
    raise AssertionError("expected UnknownChild")

fallback = app.get_value("field9", "<missing>")
assert fallback == "<missing>"

print("\nIterate fields:")
for name, child in app.items():
    print(f"  {name}: value={child.get_value()!r} default={child.get_default()!r}")

print("\nOK")
