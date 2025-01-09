import pytest

# This test explore the nested use cases

from pprint import pprint
from superconf.configuration import Configuration, Field, Environment
import classyconf.exceptions
from classyconf.loaders import Dict


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

class Resource(Configuration):
    "Represent resources"

    # class Meta:
    #     loaders=[Dict(RESOURCES)]
        
    location = Field(default="MISSING LOCATION")
    owner = Field(default="MISSING OWNER")



class ResourcesCtl(Configuration):
    "Represent resources"

    class Meta:
        loaders=[Dict(RESOURCES)]
        children_class = Resource


class AppConfig(Configuration):
    "Main app config"


    # meta__custom_field = "My VALUUUUuuueeeee 555555"

    # class Meta:
    #     cache = False
    #     children_class = Resources
        # custom_field = "My VALUUUUuuueeeee"

    resources = Field(
        children_class=ResourcesCtl, 
    )



app = AppConfig()


o = app["resources"].get_values()
pprint(o)
assert "laptop" in o

assert False




# Test to get all values
# ==================

ress = {
    'resources': {},
    }


o = app["resources"].get_values(lvl=2)
pprint (o)


assert o != ress, "Please fix empty resources"

o = app.get_values(lvl=2)
pprint (o)




# Ensure default resources are created




print("All tests OK")
