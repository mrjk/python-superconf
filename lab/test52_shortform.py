import logging
from pprint import pprint

from superconf import (
    ConfigurationDict,
    ConfigurationObj,
    FieldConf,
    FieldDict,
    FieldList,
    FieldString,
)
from superconf.exceptions import InvalidFieldOption

# logging.basicConfig(level=logging.DEBUG)


class AppFeature(ConfigurationObj):
    """Feature object"""

    class Meta:
        extra_fields = True

    name = FieldString(help="Feature name")
    group = FieldString(help="Default group", default="__base__")


# class AppFeatures(ConfigurationDict):
#     """App Features Feature"""

#     class Meta:
#         children_class = AppFeature


class App(ConfigurationObj):
    """Main App"""

    class Meta:
        extra_fields = False

    # Application configuration
    # default_features = FieldList(help="default features")
    # resource_model = FieldDict(help="resource model")

    # This is the long form
    # features = FieldConf(AppFeatures)

    # This is the short form
    features = FieldConf(
        ConfigurationDict,
        help="THIS IS MY ITEM",
        children_class=AppFeature,
        # extra_fields=True,
    )


# Test failure for extra fields, since there is not such option in ConfigurationDict
try:
    features = FieldConf(
        ConfigurationDict,
        extra_fields=True,
    )
    assert False, "Should have raised an excveption"
except InvalidFieldOption:
    pass


# pprint(ConfigurationDict.__node_config__.__dict__)
# pprint(ConfigurationObj.__node_config__.__dict__)


app_payload = {
    "features": {
        "feat1": {
            "name": "feat1",
            "group": "group1",
        },
        "feat2": {
            "name": "feat2",
            "group": "group2",
            "fake_feat": "TUTU",
        },
    }
}

app = App(value=app_payload)

# pprint(app)
# pprint(app.get_value())

# pprint(app.features)
# pprint(app.features.get_value())
# pprint(app.features)
# pprint(app.features.__dict__)

print("FEATURE HELP", app.features.__node_help__)
for feature in app.features:

    print("FEATURE", type(feature), feature)
    assert isinstance(feature, AppFeature)
    print("FEATURE HELP", feature.__node_help__)


print("All tests OK")
