"""FieldConf shortform: ConfigurationDict + children_class inline."""

from pprint import pprint

from superconf import ConfigurationDict, ConfigurationObj, FieldConf, FieldString
from superconf.exceptions import InvalidFieldOption


class Feature(ConfigurationObj):
    """One feature entry."""

    class Meta:
        extra_fields = True

    name = FieldString(help="Feature name")
    group = FieldString(default="__base__", help="Default group")


class App(ConfigurationObj):
    """App using FieldConf shortform (no intermediate dict subclass)."""

    class Meta:
        extra_fields = False

    features = FieldConf(
        ConfigurationDict,
        help="Named features",
        children_class=Feature,
    )


# extra_fields is not valid on ConfigurationDict via FieldConf
try:
    FieldConf(ConfigurationDict, extra_fields=True)
except InvalidFieldOption:
    print("InvalidFieldOption: extra_fields not allowed on ConfigurationDict FieldConf")
else:
    raise AssertionError("expected InvalidFieldOption")


app = App(
    value={
        "features": {
            "feat1": {"name": "feat1", "group": "group1"},
            "feat2": {"name": "feat2", "group": "group2", "fake_feat": "TUTU"},
        }
    }
)

print("\nFeatures:")
pprint(app.features.get_value())
print(f"features help: {app.features.__node_help__}")

for name, feature in app.features.items():
    assert isinstance(feature, Feature)
    print(f"  {name}: name={feature.name!r} group={feature.group!r}")

assert len(app.features) == 2
assert app.features.feat2.get_value("fake_feat") == "TUTU"

print("\nOK")
