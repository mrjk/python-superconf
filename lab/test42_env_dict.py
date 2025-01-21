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
from superconf.loaders import Dict, Environment, EnvPrefix

# from superconf.wrapper import (
#     ConfigurationWrapper,
#     ConfigurationDictWrapper,
#     ConfigurationListWrapper,
# )

# from superconf.configuration_dev import ConfigurationList


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


class AppBackends(ConfigurationDict):
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

    backends = FieldConf(AppBackends, default={"mysql": None})


ENV_VARS = {
    "MY_APPLICATION__CONFIG__MAX": "424242",
    "MY_APPLICATION__CONFIG__ANALYTICS": "1",
    "MY_APPLICATION__BACKENDS__MYBACKEND__ENABLED": "True",
    "MY_APPLICATION__BACKENDS__REDIS__PORT": "8080",
    "MY_APPLICATION__BACKENDS__REDIS__USER": "MArCEEEl",
}

os.environ.update(ENV_VARS)


app = App()


pprint(app.__dict__)


OUT = app.get_values()
pprint(OUT)

print("==============")
EXPECTED = {
    "backends": {
        "mybackend": {
            "enabled": True,
            "host": "localhost",
            "password": "admin",
            "port": NOT_SET,
            "user": "admin",
        },
        "redis": {
            "enabled": False,
            "host": "localhost",
            "password": "admin",
            "port": 8080,
            "user": "MArCEEEl",
        },
    }
}
OUT = app.get_values()
pprint(OUT)
assert OUT == EXPECTED

assert app["backends"]["redis"]["user"] == "MArCEEEl"
assert app["backends"]["mybackend"]["port"] == NOT_SET
assert app["backends"]["mybackend"]["enabled"] == True


OUT = app["backends"]["redis"].get_values()
EXPECTED = {
    "enabled": False,
    "host": "localhost",
    "password": "admin",
    "port": 8080,
    "user": "MArCEEEl",
}
pprint(OUT)
assert OUT == EXPECTED

# pprint(app.config.__dict__)

# # pprint()
# pprint(app.config["analytics"])


print("All tests O WIPK")
