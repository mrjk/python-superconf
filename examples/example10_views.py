"""Layered View with ConfigSource / EnvSource / DictSource."""

from pprint import pprint

from superconf import (
    TWELVE_FACTOR_ORDER,
    ConfigSource,
    ConfigurationObj,
    DictSource,
    EnvSource,
    FieldBool,
    FieldInt,
    FieldString,
    View,
)


class AppConfig(ConfigurationObj):
    """Minimal app config for view demo."""

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


defaults = AppConfig()
cli_overlay = {"name": "from-cli", "count": 25}
environ = {
    "APP__ENABLED": "false",
    "APP__COUNT": "42",
}

view = View(order=TWELVE_FACTOR_ORDER)
view.add(ConfigSource("defaults", defaults, nodefaults=False))
view.add(EnvSource("env", prefix="APP", environ=environ))
view.add(DictSource("cli", cli_overlay))

print("Layer order:")
pprint(view.get_order())
print("\nLayers:")
pprint(view.load_layers())

merged = view.materialize()
print("\nMaterialized (raw layers, env still strings):")
pprint(merged)
print("\nExplain enabled:")
pprint(view.explain("enabled"))

assert merged["name"] == "from-cli"
assert merged["count"] == 25
assert merged["enabled"] == "false"

app = AppConfig(value=merged)
print("\nTyped AppConfig:")
pprint(app.get_value())
assert app.name == "from-cli"
assert app.count == 25
assert app.enabled is False

print("\nOK")
