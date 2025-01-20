
# pylint: skip-file

import sys
from pprint import pprint

import pytest

import superconf.exceptions
from superconf.configuration import (
    NOT_SET,
    Configuration,
    ConfigurationDict,
    Environment,
    Field,
    FieldConf,
)
from superconf.loaders import Dict

# This test explore the nested use cases, WITHOUT defaults


# Resource list
RESOURCES1 = {
    "laptop": {
        "location": "home",
        "owner": "rob",
    },
    "wifi-ap": {
        "location": "home2",
    },
}
RESOURCES2 = {
    "phone": {},
    "camera": None,
}

CONFIG_MERGED = {"resources": RESOURCES1 | RESOURCES2}
RESOURCES_COUNT = len(CONFIG_MERGED["resources"])


class Resource(Configuration):
    "Represent resources"

    class Meta:
        extra_fields = False
        default = {
            "location": "MISSING LOCATION2",
            "owner": "MISSING OWNER",
        }

    location = Field()
    owner = Field()


class ResourcesCtl(ConfigurationDict):
    "Represent resources"

    class Meta:
        children_class = Resource


class AppConfig(Configuration):
    "Main app config"

    class Meta:
        # default = {"resources": {"res1": {"owner": "bob", "location": "BLIHH"}}}
        cache = True

    resources = FieldConf(
        ResourcesCtl,
        help="List of resources",
    )

    test_config = Field(default="Yeahhh")
    test_config2 = Field()


# App & Resources creation with Value
# =============================

# Create app with preset values
app = AppConfig(value=CONFIG_MERGED)


# Ensure regular fields with defaults works
assert app["test_config"] == "Yeahhh"

# Ensure regular fields with defaults works
pprint( app["test_config2"])
# pprint( id(app["test_config2"]), id(NOT_SET))
assert app["test_config2"] == NOT_SET
# assert app["test_config2"] is NOT_SET # TOFIX !!!!

# Ensure missing keys raise KeyError
with pytest.raises(KeyError):
    o = app["test_config3"]


# Fetch resource object
o_resources = app["resources"]

# Ensure we get an object instance, not the value
assert isinstance(o_resources, ResourcesCtl)

# Validate dict value has correct number of children
assert len(o_resources.get_values()) == RESOURCES_COUNT


# Resources testing
# =============================

# Ensure full values are still full
o_laptop = o_resources["laptop"]
assert isinstance(o_laptop, Resource)
assert o_laptop.get_values() == RESOURCES1["laptop"]

# Ensure value retrieval works as expected
assert o_laptop["location"] == "home"
assert o_laptop["owner"] == "rob"


# Ensure values are correctly defaulted on partial items
o_wifi = o_resources["wifi-ap"]
assert isinstance(o_wifi, Resource)
assert o_wifi.get_values() is not RESOURCES1["wifi-ap"]
assert o_wifi.get_values() == RESOURCES1["wifi-ap"]  # TOFIX

# Ensure defaults are correctly set on partial values
o_phone = o_resources["phone"]
# pprint (o_phone.__dict__)

pprint(o_phone["location"])
assert o_phone["location"] == "MISSING LOCATION2"
assert o_phone["owner"] == "MISSING OWNER"

# Ensure default on None values
o_camera = o_resources["camera"]
assert o_camera["location"] == "MISSING LOCATION2"
assert o_camera["owner"] == "MISSING OWNER"


print("All tests OK")
