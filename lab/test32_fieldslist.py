# pylint: skip-file

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
from superconf.loaders import Dict

# from superconf.configuration_dev import ConfigurationList


# This test explore the nested use cases, WITH defaults


# Test extra Fields Dict
# =============================

print("\n\n================ List Fields ===========\n\n")


class AppList(ConfigurationList):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = False
        default = [
            {"key1": "item1"},
            {"key2": "item2"},
            {"key3": "item3"},
        ]
        children_class = ConfigurationDict


app1 = AppList()

EXPECTED = [{"key1": "item1"}, {"key2": "item2"}, {"key3": "item3"}]


# pprint(app1.__dict__)

# pprint(app1.get_values())


# pprint(app1[1].get_values())


assert app1.get_values() == EXPECTED


print("All tests O WIPK")
