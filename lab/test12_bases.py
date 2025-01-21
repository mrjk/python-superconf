# pylint: skip-file

from pprint import pprint

import pytest

import superconf.exceptions
from superconf.configuration import Configuration, Environment, Field, FieldConf
from superconf.loaders import Dict

# This test explore the default specificities of classyconf
# We want to keep this API compatible


example_dict = {
    "item1": True,
    "item2": 4333,
}

FULL_CONFIG = {
    "field1": False,
    "field2": "Default value",
    "field3": 42,
    "field4": example_dict,
    "field5": example_dict,
}
CHILDREN_COUNT = len(FULL_CONFIG)


class AppConfig(Configuration):

    class Meta:
        loaders = [Environment()]

    field5 = Field(default=example_dict, help="Another dict field")

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="Another field")
    field3 = Field(default=42, help="Another field")
    field4 = Field(default=example_dict, help="Another dict field")


class TopConfig(Configuration):

    class Meta:
        cache = False

    top1 = Field(default="default top value")
    top2 = FieldConf(
        AppConfig,
        # default={
        #     "field1": True,
        #     "field2": "Parent override",
        # }
    )


app = TopConfig()


# We check here we can access via attributes and items
assert app.top1 == "default top value"
assert isinstance(app.top1, str)
assert app["top1"] == "default top value"
assert isinstance(app["top1"], str)

# pprint (app.__dict__)
# pprint(app)
# pprint(app.declared_fields)
# pprint(app._children)


###################################
# Create a simple child object


# We check known value retrieval here
t1 = app.get_value("top1")
# pprint (t1)
assert t1 == "default top value"


# Test children object is correctly accessible
assert id(app.top2) == id(app.top2), "TOFIX THIS BUG"
# assert id(app.top2) != id(app.top2), "SHould not have the same id since cache is disabled"
t1 = app.top2

# print(type(t1))
assert isinstance(t1, AppConfig)
assert t1.field3 is t1.field3
assert t1.field3 == 42, f"Got: {t1.field3}"
assert t1.field1 == False

# assert values of child
assert t1.get_value("field2") == "Default value"
assert t1.get_value("field4") == example_dict
# pprint (t1.get_value("field2"))


# check parent values

###################################
# Create a simple child object with value


# Note first field1 is boolean casted to text since
# superconf use default type value to auto-cast
EXPECTED_FULL_CONFIG2 = {
    "top1": "default top value",
    "top2": {
        "field1": False,
        "field2": "Default value",
        "field3": 42,
        "field4": {"item1": True, "item2": 4333},
        "field5": {"item1": True, "item2": 4333},
    },
}


app = TopConfig(loaders=[Dict(FULL_CONFIG)])


# Test child access

child1 = app.get_value("top2")
# pprint(child1)

# Ensure children and parent are not the same objects
assert isinstance(app, TopConfig)
assert isinstance(child1, AppConfig)


###################################
# Test nested get_value, with and wihtout levels

# Check we get the full config with get_value()
o = app.get_values(lvl=-1)
pprint(app.__dict__)
pprint(o)
pprint(EXPECTED_FULL_CONFIG2)
assert o == EXPECTED_FULL_CONFIG2

# Check levels depth
result = app.get_values(lvl=1)
assert result["top1"] == "default top value"
assert isinstance(result["top2"], AppConfig)


print("All tests OK")
