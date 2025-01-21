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

# This test explore the nested use cases, WITH defaults


# extra_fiels tests
# =============================


print("=============== VAlidate extra_children")


class ResourceFailWithUnknownArgs(Configuration):
    "Represent resources, alternative way"

    class Meta:
        default = {
            "field1": "MISSING LOCATION2",
            "field3": "Config Error",
        }
        # extra_fields = True
        extra_fields = False

    field1 = Field()
    field2 = Field()


# This should fail since namepace3 is not declared
with pytest.raises(superconf.exceptions.UnknownExtraField):
    f1 = ResourceFailWithUnknownArgs()
    # pprint(f1)
    # pprint(f1.__dict__)


class ResourceOKWithUnknownArgs(Configuration):
    "Represent resources, alternative way"

    class Meta:
        default = {
            "field1": "MISSING LOCATION2",
            "field3": "Config Error",
        }
        extra_fields = True
        # extra_fields = False

    field1 = Field()
    field2 = Field()


# This should fail since field3 is not declared but extra_fields is enabled
f2 = ResourceOKWithUnknownArgs()

EXPECTED = {"field1": "MISSING LOCATION2", "field2": NOT_SET, "field3": "Config Error"}
assert f2.get_values() == EXPECTED


# extra_fiels tests with children class
# =============================


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


# class Resource1(Configuration):
#     "Represent resources"

#     # class Meta:
#     #     loaders=[Dict(RESOURCES1)]

#     location = Field(default="MISSING LOCATION1")
#     owner = Field(default="MISSING OWNER1")


class Resource2(Configuration):
    "Represent resources, alternative way"

    class Meta:
        default = {
            "location": "MISSING LOCATION2",
            "owner": "MISSING OWNER2",
            "namespace3": "Absent",
        }
        extra_fields = True
        # extra_fields = False

    location = Field()
    owner = Field()
    namespace = Field(default="default_ns")
    namespace2 = Field()


# class Resource3(Configuration):
#     "Represent resources dict, with unknown fields"

#     class Meta:
#         default = {
#             "location": "MISSING LOCATION2",
#             "owner": "MISSING OWNER2",
#         }


class ResourcesCtl(ConfigurationDict):
    "Represent resources"

    class Meta:
        # loaders = [ Dict(RESOURCES1) ]
        # default = {"res22": {"owner": "bob", "location": "BLIHH"}}
        default = {"res22": None}
        children_class = Resource2


class AppConfig(Configuration):
    "Main app config"

    class Meta:
        # default = {}
        default = {
            # "resources": {
            #     "res1": {"owner": "bob", "location": "BLIHH"}
            #     }
        }
        cache = True

    resources = FieldConf(
        ResourcesCtl,
        # default = {"res33": {"owner": "bob", "location": "BLIHH"}},
        default={"res33": NOT_SET},
        help="List of resources",
    )


# App & Resources creation with Value
# =============================

# Create app with preset values
app = AppConfig()


print("=============== APP")
pprint(app.__dict__)
pprint(app.get_values())

EXPECTED = {
    "resources": {
        "res33": {
            "location": "MISSING LOCATION2",
            "namespace": "default_ns",
            "namespace2": NOT_SET,
            "namespace3": "Absent",
            "owner": "MISSING OWNER2",
        }
    }
}
assert app.get_values() == EXPECTED


print("=============== RESOURCES")
res = app["resources"]
# pprint(res.__dict__)
# pprint(res.get_values())
EXPECTED = {
    "res33": {
        "location": "MISSING LOCATION2",
        "namespace": "default_ns",
        "namespace2": NOT_SET,
        "namespace3": "Absent",
        "owner": "MISSING OWNER2",
    }
}
assert res.get_values() == EXPECTED


print("=============== RESOURCES.res33")
res1 = res["res33"]
# pprint(res1.__dict__)
# pprint(res1.get_values())

EXPECTED = {
    "location": "MISSING LOCATION2",
    "namespace": "default_ns",
    "namespace2": NOT_SET,
    "namespace3": "Absent",
    "owner": "MISSING OWNER2",
}
assert res1.get_values() == EXPECTED


print("All tests OK")
