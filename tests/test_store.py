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

from superconf.store import store_to_json

import superconf.exceptions


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
                    "yooo": "YEAHHHH",
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

    # TEst getitems
    inst3 = StoreDict(value=d2, item_class=StoreDict)

    # pprint(inst3["item1"].get_key())
    assert inst3.get_key() == ""
    assert inst3["item1"].get_key() == "item1"

    return

    "WIPPP"

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

    # assert inst3["item3"].get_key() == "item3"

    # print ("TESSSSSSSSSSSSSSSSSS")
    # inst3["item1"].explain()
    # pprint (inst3["item1"]["sub1"])

    # assert inst3["item1"]["sub1"] != None

    # print(store_to_json(inst3.explain_tree(mode="struct")))
    # assert False

    return

    assert inst3["item3"]["sub1"].get_key() == "sub1"

    t = inst3["item1"].get_envvars()
    pprint(t)
    assert False


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
