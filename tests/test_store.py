import pytest
import inspect
from logging import Logger
from pprint import pprint

# from classyconf.casts import Boolean, List, Option, Tuple, evaluate
# from classyconf.exceptions import InvalidConfiguration

# from superconf.node import NodeBase, NodeContainer, NodeMeta, NodeChildren
# from superconf.node import UNSET, DEFAULT_VALUE, UNSET_VALUE
from superconf.configuration import UNSET, DEFAULT_VALUE, UNSET_VALUE
from superconf.configuration import StoreValue, StoreDict, StoreList
from superconf.configuration import Value, ValueConf, ValueDict, ValueList

from superconf.store import store_to_json, StoreAny, StoreAuto

import superconf.exceptions as exceptions


def test_to_json():

    inst = StoreValue()
    out = inst.to_json()
    assert out == "null"


# ================================================
# Tests Class: NodeBase
# ================================================


def test_storevalue_cls_default():
    "Test a default Storevalue"

    inst = StoreValue()

    assert isinstance(inst.name, str)
    assert inst.name == ""
    assert inst.parent == None
    assert inst.fname == ""


# ================================================
# Tests Class: StoreConf
# ================================================


# ================================================
# Tests Class: StoreDict
# ================================================


def test_storedict_cls_empty():
    "Test a default Storevalue"

    # Test empty
    inst = StoreDict()

    assert inst.get_value() == {}
    assert inst.get_default() == {}
    assert inst.get_children() == UNSET


def test_storedict_cls_value_and_defaults():
    "Test a Storevalue"

    d1 = {
        "default_item1": "default_value1",
        "default_item2": "default_value2",
    }
    d2 = {
        "item1": "item1",
        "item2": "item2",
        "item3": "item3",
    }

    # Generate 3 instances
    inst1 = StoreDict(default=d1)
    inst2 = StoreDict(value=d2)
    inst3 = StoreDict(value=d2, default=d1)

    assert inst1.get_value() == d1
    assert inst1.get_default() == d1
    assert len(inst1.get_children()) == 2
    assert "default_item1" in inst1.get_children()
    assert "item1" not in inst1.get_children()

    assert inst2.get_value() == d2
    assert inst2.get_default() == {}
    assert len(inst2.get_children()) == 3
    assert "item1" in inst2.get_children()
    assert "item2" in inst2.get_children()

    assert inst3.get_value() == d2
    assert inst3.get_default() == d1
    assert len(inst3.get_children()) == 3
    assert "item1" in inst3.get_children()
    assert "item2" in inst3.get_children()


def test_storedict_cls_dunders():
    "Test a Storevalue"

    d1 = {
        "default_item1": "default_value1",
        "default_item2": "default_value2",
    }
    d2 = {
        "item1": "item1",
        "item2": "item2",
        "item3": "item3",
    }

    # TEst getitems
    inst3 = StoreDict(value=d2, default=d1)
    assert inst3["item1"].get_value() == "item1"
    assert inst3["item2"].get_value() == "item2"

    # Test iterate
    count = 0
    for ke, v in inst3:
        count += 1
    assert count == 3

    # Test len
    assert len(inst3) == 3

    # Test contain
    assert "item1" in inst3
    assert "item4" not in inst3


def test_storedict_get_key_nested():
    "Test a Storevalue"

    d2 = {
        "item1": {
            "sub1": {
                "sub11": {
                    "sub111": {
                        "yooo": "YEAHHHH",
                    },
                    "sub112": {
                        "yooo": "YEAHHHH",
                    },
                }
            },
        },
        "item2": {
            "sub2": {"sub22": {}},
        },
        "item3": {
            "sub3": {"sub33": {}},
        },
    }

    d3 = {
        # Mixed content
        "item4": ["val1", "val2"],
        "item5": "value5",
    }
    d3.update(d2)

    inst3 = StoreDict(value=d3, item_class=StoreAuto)
    # print(store_to_json(inst3.explain_tree(mode="struct")))

    assert inst3["item1"]["sub1"].get_key() == "sub1"
    assert inst3["item1"]["sub1"]["sub11"].get_key() == "sub11"

    assert inst3["item1"].get_key(mode="parents") == ".item1"
    assert inst3["item1"]["sub1"].get_key(mode="parents") == ".item1.sub1"
    assert (
        inst3["item1"]["sub1"]["sub11"].get_key(mode="parents") == ".item1.sub1.sub11"
    )
    assert (
        inst3["item3"]["sub3"]["sub33"].get_key(mode="parents") == ".item3.sub3.sub33"
    )


# ================================================
# Tests Class: StoreList
# ================================================


def test_storelist_cls_empty():
    "Test a default Storevalue"

    # Test empty
    inst = StoreList()

    assert inst.get_value() == []
    assert inst.get_default() == []
    assert inst.get_children() == UNSET


def test_storelist_cls_value_and_defaults():
    "Test a Storevalue"

    d1 = ["default_item1", "dfault_item2"]
    d2 = ["item1", "item2", "item3"]

    # Generate 3 instances
    inst1 = StoreList(default=d1)
    inst2 = StoreList(value=d2)
    inst3 = StoreList(value=d2, default=d1)

    assert inst1.get_value() == d1
    assert inst1.get_default() == d1
    assert len(inst1.get_children()) == 2
    assert "0" in inst1.get_children()
    assert "2" not in inst1.get_children()

    assert inst2.get_value() == d2
    assert inst2.get_default() == []
    assert len(inst2.get_children()) == 3
    assert "0" in inst2.get_children()
    assert "2" in inst2.get_children()

    assert inst3.get_value() == d2
    assert inst3.get_default() == d1
    assert len(inst3.get_children()) == 3
    assert "0" in inst3.get_children()
    assert "2" in inst3.get_children()


def test_storelist_cls_dunders():
    "Test a Storevalue"

    d1 = ["default_item1", "dfault_item2"]
    d2 = ["item1", "item2", "item3"]

    # TEst getitems
    inst3 = StoreList(value=d2, default=d1)
    assert inst3["0"].get_value() == "item1"
    assert inst3["1"].get_value() == "item2"

    # Test iterate
    count = 0
    for ke, v in inst3:
        count += 1
    assert count == 3

    # Test len
    assert len(inst3) == 3

    # Test contain
    assert "0" in inst3
    assert "8" not in inst3


# ================================================
# Tests Values: Base and mixed values
# ================================================


def test_config_base_types():
    "Test each config types"

    c_string1 = "string_value1"

    c_dict1 = {"key1": "dict_value1"}

    c_list1 = ["list_value1"]

    # Test generic
    def test_generic(cls):
        t1 = cls(value=c_string1)
        t2 = cls(value=c_dict1)
        t3 = cls(value=c_list1)

        # print(store_to_json(t1.explain_tree(mode="struct")))
        # print(store_to_json(t2.explain_tree(mode="struct")))
        # print(store_to_json(t3.explain_tree(mode="struct")))

        assert t1.get_value() == "string_value1"
        assert t2["key1"].get_value() == "dict_value1"
        assert t3["0"].get_value() == "list_value1"

    test_generic(StoreAuto)
    test_generic(StoreAny)

    # Test specific
    StoreValue(value=c_string1)
    StoreDict(value=c_dict1)
    StoreList(value=c_list1)

    # Test invalid matches
    def test_invalid(cls, value):
        try:
            cls(value=value)
            assert False, f"Should have throwh error for {cls} with {value}"
        except exceptions.InvalidValueType:
            pass

    test_invalid(StoreDict, c_list1)
    test_invalid(StoreDict, c_string1)
    test_invalid(StoreList, c_dict1)
    test_invalid(StoreList, c_string1)

    # assert False, "YOO"


def test_config_base_mixed_types():
    "Test each config types"

    c_string1 = "string_value1"

    c_dict1 = {"key1": "dict_value1"}

    c_list1 = ["list_value1"]

    c_mixed = {
        "mixed1": c_string1,
        "mixed2": c_dict1,
        "mixed3": c_list1,
    }

    # Test generic
    def test_generic(cls):
        t = cls(value=c_mixed)
        # t2 = cls(value=c_dict1)
        # t3 = cls(value=c_list1)

        # print(store_to_json(t.explain_tree(mode="struct")))
        # pprint(t.get_value())
        # print(store_to_json(t2.explain_tree(mode="struct")))
        # print(store_to_json(t3.explain_tree(mode="struct")))

        assert t.get_value() == c_mixed
        # assert t2["key1"].get_value() == "dict_value1"
        # assert t3["0"].get_value() == "list_value1"

        return t

    t1 = test_generic(StoreAuto)
    t2 = test_generic(StoreAny)

    assert len(t1.get_children()) == 3
    assert len(t2.get_children()) == 3

    assert len(t1["mixed1"].get_children()) == 0
    assert len(t2["mixed1"].get_children()) == 0

    assert len(t1["mixed2"].get_children()) == 1
    assert len(t2["mixed2"].get_children()) == 0

    assert len(t1["mixed3"].get_children()) == 1
    assert len(t2["mixed3"].get_children()) == 0


def test_config_base_nested_types():
    "Test each config types"

    c_dict1 = {"key1": "dict_value1", "key2": "dict_value2"}

    c_list1 = ["list_value1"]

    c_dict_nested = {
        "nested1": c_dict1,
        "nested2": c_dict1,
        "nested3": c_dict1,
    }
    c_list_nested = [
        c_list1,
        c_list1,
        c_list1,
    ]

    # Test generic
    def test_generic(cls):
        t1 = cls(value=c_dict_nested)
        t2 = cls(value=c_list_nested)
        # t3 = cls(value=c_list1)

        print(store_to_json(t1.explain_tree(mode="struct")))
        # pprint(t.get_value())
        print(store_to_json(t2.explain_tree(mode="struct")))
        # print(store_to_json(t3.explain_tree(mode="struct")))

        assert t1.get_value() == c_dict_nested
        assert t2.get_value() == c_list_nested
        # assert t3["0"].get_value() == "list_value1"

        return t1, t2

    t1, t2 = test_generic(StoreAuto)
    # t2 = test_generic(StoreAny)

    assert len(t1.get_children()) == 3
    assert len(t2.get_children()) == 3

    assert len(t1["nested1"].get_children()) == 2
    assert len(t2["0"].get_children()) == 1

    assert len(t1["nested2"].get_children()) == 2
    assert len(t2["1"].get_children()) == 1

    assert len(t1["nested3"].get_children()) == 2
    assert len(t2["2"].get_children()) == 1
    # assert False
