import pytest

# This test explore the nested use cases

from pprint import pprint
from superconf.configuration import Configuration, Field, Environment
import superconf.exceptions
from superconf.loaders import Dict


# Resource list
RESOURCES = {
    "laptop": {
        "location": "home",
        "owner": "rob",
    },
    "wifi-ap": {
        "location": "home",
        "owner": "michel",
    },
}
RESOURCES2 = {
    "phone": {
        "location": "roaming",
        "owner": "rob",
    },
}

CONFIG1 = {
    "resources": RESOURCES | RESOURCES2
}

class Resource(Configuration):
    "Represent resources"

    # class Meta:
    #     loaders=[Dict(RESOURCES)]

    location = Field(default="MISSING LOCATION")
    owner = Field(default="MISSING OWNER")


class ResourcesCtl(Configuration):
    "Represent resources"

    class Meta:
        # loaders = [ Dict(RESOURCES) ]
        children_class = Resource


class AppConfig(Configuration):
    "Main app config"

    # meta__custom_field = "My VALUUUUuuueeeee 555555"

    class Meta:
        # default = {"resources": {"res1": {"owner": "bob"}}}
        cache = True

    #     cache = False
    #     children_class = Resources
    # custom_field = "My VALUUUUuuueeeee"

    resources = Field(
        children_class=ResourcesCtl,
    )


app = AppConfig(value=CONFIG1)
# app = AppConfig()

print("+++++++++++++++++++ APP")
# pprint(Dict)
# pprint(Dict.__dict__)
# pprint(app.__dict__)
# pprint(app._declared_values)

print("+++++++++++++++++++ RESOURCES")
# pprint(app["resources"])
# pprint(app["resources"].__dict__)

o = app["resources"]
assert isinstance(o, ResourcesCtl)


pprint(o.__dict__)


o = app["resources"].get_values()
pprint(o)
assert "laptop" in o

print("+++++++++++++++++++ RESOURCES.LPATOP")


# o = app["resources"]["laptop"].get_values()
o = app["resources"]["laptop"]
assert isinstance(o, Resource)
# pprint(type(o))
pprint(o.__dict__)


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


print("All tests OK")
