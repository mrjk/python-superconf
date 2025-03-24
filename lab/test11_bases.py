# pylint: skip-file
import copy
from pprint import pprint

import pytest

from superconf import ConfigurationObj, Field, Leaf, UndeclaredField, UnknownChild

# This test explore the default specificities of superconf


# Base configurations
# ==============================

# Create a base configuration
CONFIG_BASE = {
    "item1": True,
    "item2": 4333,
}

CONFIG_OVERRIDE = {
    "item1": "yeah",
    "item2": 777,
}

# Create a more moplete configuration
CONFIG_FULL1 = {
    "field1": True,
    "field2": "Custom value",
    "field3": 51,
    "field4": CONFIG_OVERRIDE,
}

CONFIG_FULL2 = {
    "field1": True,
    "field2": "config2 value",
    "field3": 3.1416,
    "field4": {
        "other1": "anything",
        "other2": None,
    },
}


# I. Configuration Object model declaration
# ==============================

# We declare a simple ConfigurationObj model with fields we know in advance. We will
# introduce later ConfigurationDict or ConfigurationList, that handle unknown fields.


class AppConfig(ConfigurationObj):
    """Model with defaults values and help messages"""

    field1 = Field(default=False, help="Toggle debugging on/off.")
    field2 = Field(default="Default value", help="Another field")
    field3 = Field(default=42, help="Another field")
    field4 = Field(default=CONFIG_BASE, help="Another dict field")


# II. Model instanciation without configuration
# ==============================

# This explains how to access the model fields, by different methods.

app = AppConfig()


# Feature - String field
# ------------------------------

# We check here we can access via attributes
assert app.field1 is False
assert isinstance(app.field1, bool)

# We check here we can access via items
assert app["field1"] is False
assert isinstance(app["field1"], bool)

# We can access the children value with get_value()
assert app.get_value("field1") is False
assert isinstance(app.get_value("field1"), bool)

# We can access children object via call syntax
assert isinstance(app("field1"), Leaf)
assert app("field1").get_value() is False


# Feature - Integer field
# ------------------------------

# We check here we can access via attributes
assert app.field2 == "Default value"
assert isinstance(app.field2, str)

# We check here we can access via items
assert app["field2"] == "Default value"
assert isinstance(app["field2"], str)

# We can access the children value with get_value()
assert app.get_value("field2") == "Default value"
assert isinstance(app.get_value("field2"), str)

# We can access children object via call syntax
assert isinstance(app("field2"), Leaf)
assert app("field2").get_value() == "Default value"


# Feature - Dict field
# ------------------------------
assert app.field4 == CONFIG_BASE
assert isinstance(app.field4, dict)


# III. Model instanciation with configuration
# ==============================

# This explain what happens when we instanciate the model with a configuration passed via value option

app = AppConfig(value=CONFIG_FULL1)


# Accessing values and defaults with methods
# ------------------------------

assert app("field1").get_value() == True
assert app("field2").get_value() == "Custom value"
assert app("field3").get_value() == 51
assert app("field4").get_value() == CONFIG_OVERRIDE


assert app("field1").get_default() == False
assert app("field2").get_default() == "Default value"
assert app("field3").get_default() == 42
assert app("field4").get_default() == CONFIG_BASE


# Feature - Validate configuration
# ------------------------------

assert app.field1 == True
assert app.field2 == "Custom value"
assert app.field3 == 51
assert app.field4 == CONFIG_OVERRIDE


# IV. Change or update values with set_value()
# ==============================

# We can set a new value with a dict
app.set_value(CONFIG_FULL2)

pprint(app.get_value())

# Short methods
assert app.field1 == True
assert app.field2 == "config2 value"
assert app.field3 == 3.1416
assert app.field4 == CONFIG_FULL2["field4"]

# Long methods
assert app("field1").get_value() == True
assert app("field2").get_value() == "config2 value"
assert app("field3").get_value() == 3.1416
assert app("field4").get_value() == CONFIG_FULL2["field4"]

# Accessing defaults can only be done with methods
assert app("field1").get_default() == False
assert app("field2").get_default() == "Default value"
assert app("field3").get_default() == 42
assert app("field4").get_default() == CONFIG_BASE

# Eventually, we can change a single child value

NEW_FIELD_VALUE = 4242
app("field3").set_value(NEW_FIELD_VALUE)
assert app("field3").get_value() == NEW_FIELD_VALUE


# V. Accessing unknown values and exceptions
# ==============================

# Since model should be known in advance, an exception is raised if we try to access an unknown value.

# With attributes
try:
    out = app.field9
except AttributeError:
    pass
else:
    assert False, "Should raise AttributeError"


# With items
try:
    out = app["field9"]
except KeyError:
    pass
else:
    assert False, "Should raise KeyError"


# With get_value()
try:
    out = app.get_value("field9")
except UndeclaredField:
    pass
else:
    assert False, "Should raise UndeclaredField"

# With get_value() and default value
out = app.get_value("field9", "<UNKNOWN_FIELD>")
assert out == "<UNKNOWN_FIELD>"


# With call syntax
try:
    out = app("field9")
except UnknownChild:
    pass
else:
    assert False, "Should raise UnknownChild"


# VI. Iterating on fields
# ==============================

# With get_value()
out_children = {}
out_values = {}
out_defaults = {}
for name, child in app.items():
    assert isinstance(child, Leaf)
    out_children[name] = child

    value = child.get_value()
    assert not isinstance(value, Leaf)
    out_values[name] = value

    default = child.get_default()
    assert not isinstance(default, Leaf)
    out_defaults[name] = default

print("Number of fields:", len(out_children))
print("Childrens:")
pprint(out_children)
print("Defaults:")
pprint(out_defaults)

# Preapre result assertion
EXPECTED_RESULT = copy.deepcopy(CONFIG_FULL2)
EXPECTED_RESULT["field3"] = NEW_FIELD_VALUE

print("Expected Values:")
pprint(EXPECTED_RESULT)

print("Values:")
pprint(out_values)


assert len(out_children) == len(EXPECTED_RESULT)
assert set(out_children.keys()) == set(EXPECTED_RESULT.keys())
assert out_values == EXPECTED_RESULT


print("All tests OK")


############ EOF
