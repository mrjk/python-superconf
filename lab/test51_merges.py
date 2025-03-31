# pylint: skip-file

import sys
from pprint import pprint

import pytest

import superconf.exceptions
from superconf.common import DEFAULT, FAIL, NOT_SET
from superconf.configuration import (
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
)
from superconf.fields import (  # FieldOption,
    Field,
    FieldBool,
    FieldConf,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldList,
    FieldString,
    FieldTuple,
)

# from superconf.loaders import Dict

# from superconf.configuration_dev import ConfigurationList


# This test explore the nested use cases, WITH defaults


# Test extra Fields Dict
# =============================


class AppConfig(ConfigurationObj):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = False
        # default = [
        #     {"key1": "item1"},
        #     {"key2": "item2"},
        #     {"key3": "item3"},
        # ]
        # children_class = ConfigurationDict

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


class AppDict(ConfigurationDict):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = False
        children_class = AppConfig


def test_merge_for_configuration():

    # Test1: Test merge for ConfigurationObj
    app1_val = {"name": "toto", "count": 25}
    app2_val = {"name": "titi", "enabled": False}

    app1 = AppConfig(value=app1_val)
    app2 = AppConfig(value=app2_val)

    # pprint(app1.get_values())
    # pprint(app2.get_values())

    # test merge for dicts
    out = app1.merge(app2)
    assert isinstance(out, AppConfig)

    EXPECTED = {"count": 10, "enabled": False, "name": "titi"}
    # pprint(out.get_values())
    assert out.get_values() == EXPECTED


def test_merge_for_configuration_dict():
    # Test2: Test merge for ConfigurationDict
    app1_val = {
        "app1": {"name": "toto", "count": 25},
        # "app2": {"name": "titi", "enabled": False},
    }
    app2_val = {
        "app1": {"name": "tata"},
        # "app3": {"name": "tutu", "enabled": True},
    }

    print("PREPARE THINGS")
    appdict_1 = AppDict(value=app1_val)
    appdict_2 = AppDict(value=app2_val)

    print("MERGE THINGS")
    out = appdict_1.merge(appdict_2)
    assert isinstance(out, AppDict)

    print("\n\n\nCHECK RESULT")
    pprint(out.get_values())
    EXPECTED = {
        "app1": {"count": 25, "enabled": True, "name": "tata"},
        "app2": {"count": 10, "enabled": False, "name": "titi"},
        "app3": {"count": 10, "enabled": True, "name": "tutu"},
    }

    assert out.get_values() == EXPECTED


# test_merge_for_configuration()
# test_merge_for_configuration_dict()

print("All tests OK")
