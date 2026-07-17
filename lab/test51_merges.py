# pylint: skip-file

from pprint import pprint

from superconf.common import (
    MERGE_APPEND,
    MERGE_KEEP,
    MERGE_OVERRIDE,
    MERGE_OVERRIDE_ABSENT,
    MERGE_OVERRIDE_NON_NULL,
    MERGE_OVERRIDE_PRESENT,
    MERGE_PREPEND,
    MERGE_REPLACE,
    MergeStrategy,
)
from superconf.configuration import (
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
)
from superconf.fields import (  # FieldOption,
    Field,
    FieldBool,
    FieldInt,
    FieldList,
    FieldString,
)

# This test explore the nested use cases, WITH defaults


# Test extra Fields Dict
# =============================


class AppConfig(ConfigurationObj):
    "Tests types"

    name = FieldString(default="default_toto")
    enabled = FieldBool(default=True)
    count = FieldInt(default=999)


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

    # test merge for dicts
    out = app1.merge(app2)
    assert isinstance(out, AppConfig)

    EXPECTED = {"count": 25, "enabled": False, "name": "titi"}
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
    EXPECTED = {
        "app1": {"count": 64, "enabled": True, "name": "tata"},
        "app2": {"count": 999, "enabled": False, "name": "titi"},
        "app3": {"count": 999, "enabled": True, "name": "tutu"},
    }

    pprint(EXPECTED)
    pprint(out.get_value())

    assert out.get_value() == EXPECTED


def test_merge_dict_replace_and_keep():
    class Cfg(ConfigurationObj):
        class Meta:
            merge = MERGE_REPLACE

        name = FieldString(default="left")
        count = FieldInt(default=1)

    left = Cfg(value={"name": "a", "count": 10})
    right = Cfg(value={"name": "b"})
    assert left.merge(right).get_value() == right.get_value()

    class CfgKeep(ConfigurationObj):
        class Meta:
            merge = "keep"  # string form

        name = FieldString(default="left")
        count = FieldInt(default=1)

    left = CfgKeep(value={"name": "a", "count": 10})
    right = CfgKeep(value={"name": "b"})
    assert left.merge(right).get_value() == left.get_value()
    assert left.__node_merge__ == MergeStrategy.KEEP


def test_merge_strategy_enum_and_string():
    class CfgEnum(ConfigurationObj):
        class Meta:
            merge = MergeStrategy.REPLACE

        name = FieldString(default="left")

    class CfgStr(ConfigurationObj):
        class Meta:
            merge = "replace"

        name = FieldString(default="left")

    left_e = CfgEnum(value={"name": "a"})
    right_e = CfgEnum(value={"name": "b"})
    left_s = CfgStr(value={"name": "a"})
    right_s = CfgStr(value={"name": "b"})

    assert left_e.__node_merge__ is MergeStrategy.REPLACE
    assert left_s.__node_merge__ is MergeStrategy.REPLACE
    assert left_e.merge(right_e).get_value() == left_s.merge(right_s).get_value()


def test_merge_dict_override_present_absent():
    class Cfg(ConfigurationObj):
        class Meta:
            merge = MERGE_OVERRIDE_PRESENT
            extra_fields = True

        name = FieldString(default="left")
        count = FieldInt(default=1)

    left = Cfg(value={"name": "a", "count": 10})
    right = Cfg(value={"name": "b", "extra": 99})
    out = left.merge(right)
    # present keys updated; keys only in other ignored
    assert out.get_value()["name"] == "b"
    assert out.get_value()["count"] == 10
    assert "extra" not in out.get_value()

    class CfgAbsent(ConfigurationObj):
        class Meta:
            merge = MERGE_OVERRIDE_ABSENT
            extra_fields = True

        name = FieldString(default="left")
        count = FieldInt(default=1)

    left = CfgAbsent(value={"name": "a", "count": 10})
    right = CfgAbsent(value={"name": "b", "extra": 99})
    out = left.merge(right)
    # existing keys kept; absent keys added
    assert out.get_value()["name"] == "a"
    assert out.get_value()["count"] == 10
    assert out.get_value()["extra"] == 99


def test_merge_field_override_beats_meta():
    class Cfg(ConfigurationObj):
        class Meta:
            merge = MERGE_OVERRIDE

        locked = FieldInt(default=1, merge=MERGE_KEEP)
        name = FieldString(default="x")

    left = Cfg(value={"locked": 10, "name": "left"})
    right = Cfg(value={"locked": 99, "name": "right"})
    out = left.merge(right)
    assert out.get_value()["locked"] == 10
    assert out.get_value()["name"] == "right"


def test_merge_leaf_override_non_null():
    # Use Field (as_is) so None is preserved; FieldString would cast None -> "None"
    class Cfg(ConfigurationObj):
        name = Field(default="x", merge=MERGE_OVERRIDE_NON_NULL)

    left = Cfg(value={"name": "left"})
    right = Cfg(value={"name": None})
    out = left.merge(right)
    assert out.get_value()["name"] == "left"


def test_merge_list_strategies():
    class Items(ConfigurationList):
        class Meta:
            merge = MERGE_APPEND

    left = Items(value=["a", "b"])
    right = Items(value=["c"])
    assert left.merge(right).get_value() == ["a", "b", "c"]

    class ItemsPrepend(ConfigurationList):
        class Meta:
            merge = MERGE_PREPEND

    assert ItemsPrepend(value=["a"]).merge(ItemsPrepend(value=["b"])).get_value() == [
        "b",
        "a",
    ]

    class ItemsReplace(ConfigurationList):
        class Meta:
            merge = MERGE_REPLACE

    assert ItemsReplace(value=["a"]).merge(ItemsReplace(value=["b"])).get_value() == [
        "b"
    ]

    class ItemsKeep(ConfigurationList):
        class Meta:
            merge = MERGE_KEEP

    assert ItemsKeep(value=["a"]).merge(ItemsKeep(value=["b"])).get_value() == ["a"]


def test_merge_field_list_default_append():
    class Cfg(ConfigurationObj):
        tags = FieldList(default=["a"])

    left = Cfg(value={"tags": ["a", "b"]})
    right = Cfg(value={"tags": ["c"]})
    out = left.merge(right)
    assert out.get_value()["tags"] == ["a", "b", "c"]
    assert left.__node_children__["tags"].__node_merge__ == MERGE_APPEND


def test_dict_copy():

    app1_val = {
        "app1": {"name": "toto", "count": 64},
        "app2": {"name": "titi", "enabled": False},
    }

    appdict_1 = AppDict(value=app1_val)
    appdict_2 = appdict_1.copy()

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

    assert app1 is not app2
    assert app1.__node_cast__ is app2.__node_cast__
    assert app1.__node_children_classes__ is app2.__node_children_classes__

    # Deepcopy
    assert app1.__node_children__ is not app2.__node_children__


test_merge_for_configuration()
test_merge_for_configuration_dict()
test_merge_dict_replace_and_keep()
test_merge_strategy_enum_and_string()
test_merge_dict_override_present_absent()
test_merge_field_override_beats_meta()
test_merge_leaf_override_non_null()
test_merge_list_strategies()
test_merge_field_list_default_append()
test_dict_copy()
test_dict_deepcopy()

test_obj_copy()
test_obj_deepcopy()


print("All tests OK")
