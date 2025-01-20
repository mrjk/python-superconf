# pylint: skip-file

import os
import sys
from pprint import pprint

import pytest

import superconf.exceptions
from superconf.common import DEFAULT, FAIL, NOT_SET
from superconf.configuration import (
    Configuration,
    ConfigurationDict,
    ConfigurationList,
    Environment,
)

from superconf.loaders import Environment, EnvPrefix
from superconf.fields import (
    Field,
    FieldBool,
    FieldConf,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldList,
    FieldOption,
    FieldString,
    FieldTuple,
)


# from superconf.wrapper import (
#     ConfigurationWrapper,
#     ConfigurationDictWrapper,
#     ConfigurationListWrapper,
# )

# from superconf.configuration_dev import ConfigurationList

from superconf.loaders import Dict

# This test explore the nested use cases, WITH defaults

# This test object encapsulation


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

sys.exit()



class AppBackend(Configuration):
    "Application Backend"

    enabled = FieldBool(default="false", help="Enable backend")
    host = FieldString(default="localhost", help="Host")
    port = FieldInt(help="Port")
    user = FieldString(default="admin", help="User")
    password = FieldString(default="admin", help="Password")


class AppBackends(ConfigurationList):
    "Application Backends"

    class Meta:
        children_class = AppBackend

    # mysql = FieldConf(
    #     AppBackend,
    # )
    # ldap = FieldConf(
    #     AppBackend,
    # )
    # redis = FieldConf(
    #     AppBackend,
    # )


class App(Configuration):
    "Application example"

    class Meta:
        cache = True
        env_enabled = False
        env_prefix = "MY_APPLICATION"

    backends = FieldConf(
        AppBackends,
        cast = list, 
        default={"mysql": None})


ENV_VARS = {
    # "MY_APPLICATION__CONFIG__MAX": "424242",
    # "MY_APPLICATION__CONFIG__ANALYTICS": "1",
    "MY_APPLICATION__BACKENDS__1__ENABLED": "True",
    "MY_APPLICATION__BACKENDS__0__PORT": "8080",
    "MY_APPLICATION__BACKENDS__1__USER": "MArCEEEl",
}

os.environ.update(ENV_VARS)


print ("============ APP INIT START")

app = App()

print ("============ APP INIT DONE")

# pprint (app.__dict__)


OUT = app.get_values()
print ("============ APP GET VALUES")
pprint(OUT)

EXPECTED = {'backends': [{'enabled': False,
               'host': 'localhost',
               'password': 'admin',
               'port': NOT_SET,
               'user': 'admin'},
              {'enabled': True,
               'host': 'localhost',
               'password': 'admin',
               'port': NOT_SET,
               'user': 'MArCEEEl'}]}


assert isinstance(OUT["backends"], list), f"Expected a list, Got: {OUT['backends']}"
assert OUT == EXPECTED


# assert False, "WIP, fix above"

backends = app["backends"]
pprint(backends.__dict__)
OUT = app["backends"].get_values()
print ("============ BACKENDS GET VALUES")
pprint(OUT)

# assert False

print("==============")
EXPECTED = [{'enabled': False,
  'host': 'localhost',
  'password': 'admin',
  'port': NOT_SET,
  'user': 'admin'},
 {'enabled': False,
  'host': 'localhost',
  'password': 'admin',
  'port': NOT_SET,
  'user': 'MArCEEEl'}]

OUT = backends.get_values()
pprint(OUT)
# assert OUT == EXPECTED

assert backends[1]["user"] == "MArCEEEl"

assert app["backends"][0]["port"] == NOT_SET
assert app["backends"][0]["enabled"] == False
assert app["backends"][1]["enabled"] == True
# assert False, "WIP"


OUT = app["backends"][1].get_values()
EXPECTED = {'enabled': True,
 'host': 'localhost',
 'password': 'admin',
 'port': NOT_SET,
 'user': 'MArCEEEl'}

pprint(OUT)
assert OUT == EXPECTED

# pprint(app.config.__dict__)

# # pprint()
# pprint(app.config["analytics"])


# assert False, "Fix Parent object that does not return get_values correctly ..."

print("All tests O WIPK")
