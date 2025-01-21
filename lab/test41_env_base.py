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


class AppConfig(Configuration):
    "Main app config"

    class Meta:
        # default = {"resources": {"res1": {"owner": "bob", "location": "BLIHH"}}}
        cache = True
        loaders = [
            # Environment(),
            Environment(prefix="MY_SUBCONFIG_"),
        ]
        env_format = "{app}_{item}"
        env_format = "{app}_{parent}__{item}"
        env_format = "{app}_{parents}__{item}"

    max = FieldInt(default=3, help="Max instances")
    analytics = FieldBool(default="y", help="Enable analytics")


class AppBackend(Configuration):
    "Application Backend"

    # class Meta:
    #     cache = True
    #     env_enabled = False
    #     # env_prefix = None
    #     env_prefix = "MYAPPBACKENDS___"
    #     env_parents = False

    enabled = FieldBool(default="false", help="Enable backend")
    host = FieldString(default="localhost", help="Host")
    port = FieldInt(help="Port")
    user = FieldString(default="admin", help="User")
    password = FieldString(default="admin", help="Password")


class AppBackends(Configuration):
    "Application Backends"

    class Meta:
        cache = True
        env_enabled = True
        env_prefix = "prefix"
        # env_pattern = "MYAPPBACKENDS___{key}"
        # env_parents = True

    mysql = FieldConf(
        AppBackend,
    )
    ldap = FieldConf(
        AppBackend,
    )
    redis = FieldConf(
        AppBackend,
    )


class App(Configuration):
    "Application example"

    class Meta:
        cache = True
        env_name = "MY_APPLICATION"

    config = FieldConf(
        AppConfig,
    )

    backends = FieldConf(AppBackends, default={"mysql": None})


ENV_VARS = {
    "MY_APPLICATION__CONFIG__MAX": "424242",
    "MY_APPLICATION__CONFIG__ANALYTICS": "1",
    "MY_APPLICATION__PREFIX_BACKENDS__REDIS__PORT": "8080",
    "MY_APPLICATION__PREFIX_BACKENDS__REDIS__USER": "MArCEEEl",
}

os.environ.update(ENV_VARS)


print("\n\n\n++++++++++++++++++++++++++++++++++ START APPP +++++++++\n\n\n")

app = App()


print("\n\n\============== TES MAX\n\n")

print("MAX=", app.config["max"])

print("==============")
EXPECTED = {
    "backends": {
        "ldap": {
            "enabled": False,
            "host": "localhost",
            "password": "admin",
            "port": NOT_SET,
            "user": "admin",
        },
        "mysql": {
            "enabled": False,
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
    },
    "config": {"analytics": True, "max": 424242},
}
OUT = app.get_values()
pprint(EXPECTED)
pprint(OUT)

assert app.config["max"] == 424242

assert OUT == EXPECTED


print("==============")
assert app.config["max"] == 424242
assert app.config["analytics"] == True
assert app["backends"]["redis"]["user"] == "MArCEEEl"


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
