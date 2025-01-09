import pytest

# This test explore the default specificities of classyconf
# We want to keep this API compatible

from pprint import pprint
from superconf.configuration import Configuration, Field, Environment
from classyconf.loaders import Dict
import classyconf.exceptions


example_dict = {
    "item1": True,
    "item2": 4333,
}

FULL_CONFIG = {
    'field1': False,
    'field2': 'Default value',
    'field3': 42,
    'field4': example_dict,
    'field5': example_dict
}
CHILDREN_COUNT = len(FULL_CONFIG)

class AppConfig(Configuration):

    class Meta:
        loaders=[Environment()]

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="Another field")
    field3 = Field(default=42, help="Another field")
    field4 = Field(default=example_dict, help="Another dict field")
    field5 = Field(default=example_dict, help="Another dict field")


app = AppConfig(
    loaders=[
        Dict(FULL_CONFIG)
    ]
)

# We check here we can access via attributes and items
assert app.field1 is False
assert isinstance(app.field1, bool)
assert app["field1"] is False
assert isinstance(app["field1"], bool)


# We check known value retrieval here
t1 = app.get_value("field2")
assert t1 == "Default value"
t1 = app.get_value("field3")
assert t1 == 42


# We check unknown value retrieval here
t1 = app.get_value("tutu", default="SUPER")
assert t1 == "SUPER"
with pytest.raises(classyconf.exceptions.UnknownConfiguration):
    # Raise exceptions on unset values without defaults
    app.get_value("toto")


# For immutable objects, ensure we have the same ids
assert isinstance(app.field2, str)
assert app.field2 is app.field2
assert app.field2 == app.field2
assert app.field2 == "Default value"



# For mutable objects, ensure we have different ids
# Ensure we have a different object when returned, but containing the same value
assert isinstance(app.field5, dict)
assert app.field5 is not app.field5
assert app.field5 == app.field5
assert app.field5 is not example_dict
assert app.field5 == example_dict


# Ensure we can iterate on children and we have the correct number of children
count = 0
out = {}
for name, i in app:
    count += 1
    out[name] = app.get_value(i.key, default=i.default, cast=i.cast)

# ASsert we have the correct number of children and the values are correct
assert count == CHILDREN_COUNT
assert out == FULL_CONFIG
assert out is not FULL_CONFIG


print("All tests OK")