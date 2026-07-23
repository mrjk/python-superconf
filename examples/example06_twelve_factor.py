"""Load config from cli / env / defaults (12-factor style)."""

from pprint import pprint

from superconf import ConfigurationObj, FieldBool, FieldInt, FieldString, from_12factor
from superconf.twelve_factor import build_12factor_view


class AppConfig(ConfigurationObj):
    """Minimal app config with env prefix convention."""

    class Meta:
        env_prefix = "APP"

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


environ = {
    "APP__ENABLED": "false",
    "APP__COUNT": "42",
}
cli_overlay = {"name": "from-cli", "count": 25}

view = build_12factor_view(AppConfig, environ=environ, cli=cli_overlay)
print("Layer order:")
pprint(view.get_order())
print("\nLayers:")
pprint(view.load_layers())
print("\nMaterialized:")
pprint(view.materialize())
print("\nExplain enabled:")
pprint(view.explain("enabled"))

app = from_12factor(AppConfig, environ=environ, cli=cli_overlay)
print("\nTyped AppConfig:")
pprint(app.get_value())

# cli wins name/count; env wins enabled; defaults fill the rest
assert app.name == "from-cli"
assert app.count == 25
assert app.enabled is False

print("\nOK")
