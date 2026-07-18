# pylint: skip-file
"""Lab: layered View with sources (cli / env / file / defaults)."""

from pprint import pprint

from superconf.configuration import ConfigurationObj
from superconf.fields import FieldBool, FieldInt, FieldString
from superconf.sources import ConfigSource, DictSource, EnvSource
from superconf.views import TWELVE_FACTOR_ORDER, View


class AppConfig(ConfigurationObj):
    """Minimal app config for view demo."""

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


def test_view_layers():
    """Resolve values across cli, env, and schema defaults."""
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

    pprint(view.get_order())
    pprint(view.load_layers())

    merged = view.materialize()
    pprint(merged)
    pprint(view.explain("enabled"))

    # cli wins name/count; env wins enabled; defaults fill the rest
    assert merged["name"] == "from-cli"
    assert merged["count"] == 25
    assert merged["enabled"] == "false"  # env layer is still strings

    app = AppConfig(value=merged)
    assert app.name == "from-cli"
    assert app.count == 25
    assert app.enabled is False


if __name__ == "__main__":
    test_view_layers()
    print("All tests OK")
