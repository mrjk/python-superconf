import pytest
import sys

# This test explore the nested use cases, WITH defaults

from pprint import pprint
from superconf.configuration import NOT_SET, Configuration, ConfigurationDict, Field, FieldConf, Environment
import superconf.exceptions
from superconf.loaders import Dict


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

CONFIG_MERGED = {
    "resources": RESOURCES1 | RESOURCES2
}
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
            "namespace3": "Absent"
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
        children_class=ResourcesCtl,
        # default = {"res33": {"owner": "bob", "location": "BLIHH"}},
        default = {"res33": NOT_SET},
        help="List of resources",
    )



# App & Resources creation with Value
# =============================

# Create app with preset values
app = AppConfig()


print ("=============== APP")
pprint(app.__dict__)
pprint(app.get_values())


print ("=============== RESOURCES")
res = app["resources"]
pprint(res.__dict__)
pprint(res.get_values())


print ("=============== RESOURCES.res33")
res1 = res["res33"]
pprint(res1.__dict__)
pprint(res1.get_values())



# # Ensure regular fields with defaults works
# assert app["test_config"] == "Yeahhh"

# # Ensure regular fields with defaults works
# pprint( app["test_config2"])
# assert app["test_config2"] is NOT_SET

# # Ensure missing keys raise KeyError
# with pytest.raises(KeyError):
#     o = app["test_config3"]


# # Fetch resource object
# o_resources = app["resources"]

# # Ensure we get an object instance, not the value
# assert isinstance(o_resources, ResourcesCtl)

# # Validate dict value has correct number of children
# assert len(o_resources.get_values()) == RESOURCES_COUNT



# # Resources testing
# # =============================

# # Ensure full values are still full
# o_laptop = o_resources["laptop"]
# assert isinstance(o_laptop, Resource)
# assert o_laptop.get_values() == RESOURCES1["laptop"]

# # Ensure value retrieval works as expected
# assert o_laptop["location"] == "home"
# assert o_laptop["owner"] == "rob"


# # Ensure values are correctly defaulted on partial items
# o_wifi = o_resources["wifi-ap"]
# assert isinstance(o_wifi, Resource)
# assert o_wifi.get_values() != RESOURCES1["wifi-ap"]

# # Ensure defaults are correctly set on partial values
# o_phone = o_resources["phone"]
# pprint (o_phone.__dict__)

# pprint (o_phone["location"])
# assert o_phone["location"] == "MISSING LOCATION2"
# assert o_phone["owner"] == "MISSING OWNER"

# # Ensure default on None values
# o_camera = o_resources["camera"]
# assert o_camera["location"] == "MISSING LOCATION2"
# assert o_camera["owner"] == "MISSING OWNER"








print("All tests O WIPK")


# print("+++++++++++++++++++ LAPTOP AGIN")

# o = app["resources"]["laptop"]
# pprint(o.__dict__)
# pprint(o)

# o = app["resources"]["laptop"].reset()
# o = app["resources"]["laptop"]
# pprint(o.__dict__)
# pprint(o)


sys.exit(0)

print("+++++++++++++++++++ APP")
# pprint(Dict)
# pprint(Dict.__dict__)
# pprint(app.__dict__)
# pprint(app._declared_values)

print("+++++++++++++++++++ RESOURCES1")
# pprint(app["resources"])
# pprint(app["resources"].__dict__)

# o = app["resources"]
# assert isinstance(o, ResourcesCtl)


# pprint(o.__dict__)


# o = app["resources"].get_values()
# pprint(o)
# assert "laptop" in o

print("+++++++++++++++++++ RESOURCES1.LPATOP")


# o = app["resources"]["laptop"].get_values()
# o = app["resources"]["laptop"]
# assert isinstance(o, Resource)
# # pprint(type(o))
# pprint(o.__dict__)


o = app["resources"]["laptop"]["location"]
pprint(o)

assert o == "home", "WIP"


o = app["resources"]["laptop"].get_values()
pprint(o)
assert len(o) == 2
assert o.get("location", "MISSING KEY") == "home"


print("+++++++++++++++++++ WIPPPP ++++++++++++++++++++++++")



# assert False


# # Test to get all values
# # ==================

# ress = {
#     'resources': {},
#     }


# o = app["resources"].get_values(lvl=2)
# pprint (o)


# assert o != ress, "Please fix empty resources"

# o = app.get_values(lvl=2)
# pprint (o)


# # Ensure default resources are created
