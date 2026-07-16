# pylint: skip-file

from pprint import pprint

from superconf.configuration import (
    ConfigurationDict,
    ConfigurationObj,
)
from superconf.fields import (  # FieldOption,
    FieldBool,
    FieldInt,
    FieldString,
)

# This test explore the nested use cases, WITH defaults


# Test extra Fields Dict
# =============================


class AppConfig(ConfigurationObj):
    "Tests types"

    # class Meta:
    # Will fail on undefined casted values if true, alow NOT_SET
    # strict_cast = False
    # default = [
    #     {"key1": "item1"},
    #     {"key2": "item2"},
    #     {"key3": "item3"},
    # ]
    # children_class = ConfigurationDict

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)
    # opt_list = FieldList(default=["toto", "titi"])


class AppDict(ConfigurationDict):
    "Tests types"

    class Meta:
        children_class = AppConfig


def test_merge_for_configuration():

    # Test1: Test merge for ConfigurationObj
    app1_val = {"name": "toto", "count": 25}
    app2_val = {"name": "titi", "enabled": False}

    app1 = AppConfig(value=app1_val)
    app2 = AppConfig(value=app2_val)

    # pprint(app1.get_value())
    # pprint(app2.get_value())

    # test merge for dicts
    out = app1.merge(app2)
    assert isinstance(out, AppConfig)

    EXPECTED = {"count": 25, "enabled": False, "name": "titi"}
    # print("EXPECTED vs Result")
    # pprint(EXPECTED)
    # pprint(out.get_value())
    assert out.get_value() == EXPECTED


def test_merge_for_configuration_dict():
    # Test2: Test merge for ConfigurationDict
    app1_val = {
        "app1": {"name": "toto", "count": 64},
        "app2": {"name": "titi", "enabled": False},
    }
    app2_val = {
        "app1": {"name": "tata"},
        "app3": {"name": "tutu", "enabled": True},
    }

    print("PREPARE THINGS")
    appdict_1 = AppDict(value=app1_val)
    appdict_2 = AppDict(value=app2_val)

    print("MERGE THINGS")
    out = appdict_1.merge(appdict_2)
    assert isinstance(out, AppDict)

    print("\n\n\nCHECK RESULT")
    # pprint(out.get_value())
    EXPECTED = {
        "app1": {"count": 64, "enabled": True, "name": "tata"},
        "app2": {"count": 999, "enabled": False, "name": "titi"},
        "app3": {"count": 999, "enabled": True, "name": "tutu"},
    }

    pprint(EXPECTED)
    pprint(out.get_value())

    assert out.get_value() == EXPECTED


def test_dict_copy():

    app1_val = {
        "app1": {"name": "toto", "count": 64},
        "app2": {"name": "titi", "enabled": False},
    }

    appdict_1 = AppDict(value=app1_val)
    appdict_2 = appdict_1.copy()

    # pprint(appdict_1.__dict__)
    # pprint(appdict_2.__dict__)

    assert appdict_1 is not appdict_2
    assert appdict_1.__node_cast__ is appdict_2.__node_cast__

    # Copy
    assert appdict_1.app1 is appdict_2.app1
    assert appdict_1.__node_children__ is appdict_2.__node_children__


def test_dict_deepcopy():

    app1_val = {
        "app1": {"name": "toto", "count": 64},
        "app2": {"name": "titi", "enabled": False},
    }

    appdict_1 = AppDict(value=app1_val)
    appdict_2 = appdict_1.deepcopy()

    # pprint(appdict_1.__dict__)
    # pprint(appdict_2.__dict__)

    assert appdict_1 is not appdict_2
    assert appdict_1.__node_cast__ is appdict_2.__node_cast__

    # Deepcopy
    assert appdict_1.app1 is not appdict_2.app1
    assert appdict_1.__node_children__ is not appdict_2.__node_children__


def test_obj_copy():

    app1 = AppConfig(value={"name": "toto", "count": 64})
    app2 = app1.copy()

    assert app1 is not app2
    assert app1.name == app2.name
    assert app1.count == app2.count
    # pprint(app1.__dict__)
    # pprint(app2.__dict__)

    assert app1 is not app2
    assert app1.__node_cast__ is app2.__node_cast__
    assert app1.__node_children_classes__ is app2.__node_children_classes__

    # Copy
    assert app1.__node_children__ is app2.__node_children__


def test_obj_deepcopy():

    app1 = AppConfig(value={"name": "toto", "count": 64})
    app2 = app1.deepcopy()

    assert app1 is not app2
    assert app1.name == app2.name
    assert app1.count == app2.count
    # pprint(app1.__dict__)
    # pprint(app2.__dict__)

    assert app1 is not app2
    assert app1.__node_cast__ is app2.__node_cast__
    assert app1.__node_children_classes__ is app2.__node_children_classes__

    # Deepcopy
    assert app1.__node_children__ is not app2.__node_children__


test_merge_for_configuration()
test_merge_for_configuration_dict()
test_dict_copy()
test_dict_deepcopy()

test_obj_copy()
test_obj_deepcopy()


print("All tests OK")
