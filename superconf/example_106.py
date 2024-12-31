import logging
from pprint import pprint
import argparse

from superconf.loaders import YamlFile, UNSET, NOT_SET

from superconf.configuration import Configuration, ConfigurationDict, ConfigurationList
from superconf.configuration import ValueConf, ValueDict, ValueList, Value
from superconf.configuration import StoreValue, StoreDict, StoreList

parser = argparse.ArgumentParser(description="Does something useful.")
parser.add_argument(
    "--debug", "-d", dest="debug", default=NOT_SET, help="set debug mode"
)
args = parser.parse_args()


def test1():
    # First level testing

    # Test Core Values
    # ===========================

    print("\n\n===> Test core Value <====\n\n")

    class TestConfig1(Configuration):
        val_lib_undefaulted = Value()
        val_lib_undefaulted_via_args = Value(default="ARG_DEFAULT_OVERRIDE")

    p1 = TestConfig1()

    print("\n---TEST: Ensure core Value are correct type")
    t1 = p1["val_lib_undefaulted"]
    t2 = p1["val_lib_undefaulted_via_args"]
    assert isinstance(t1, StoreValue)
    assert isinstance(t2, StoreValue)

    print("\n---TEST: Ensure core Value has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    print(d1)
    print(d2)
    assert d1 == UNSET
    assert d2 == "ARG_DEFAULT_OVERRIDE"

    # Test Custom Values
    # ===========================

    print("\n\n===> Test custom Value <====\n\n")

    class ValueUnDefaulted(Value):
        "Simple var wihtout defaults"

    class ValueDefaulted(Value):
        "Simple var with default"

        # V1
        # _default = "DEFAULT_FROM_VALUE_CLASS 4444"

        # V2 recommended
        class Meta:
            default = "DEFAULT_FROM_VALUE_CLASS 4444"

    class TestConfig1(Configuration):
        val_lib_undefaulted = ValueUnDefaulted()
        val_lib_undefaulted_via_args = ValueUnDefaulted(default="ARG_DEFAULT_OVERRIDE")

        val_lib_defaulted = ValueDefaulted()
        val_lib_defaulted_via_args = ValueDefaulted(default="ARG_DEFAULT_OVERRIDE")

    p1 = TestConfig1()

    print("\n---TEST: Ensure custom Value are correct type")
    t1 = p1["val_lib_undefaulted"]
    t2 = p1["val_lib_undefaulted_via_args"]
    t3 = p1["val_lib_defaulted"]
    t4 = p1["val_lib_defaulted_via_args"]
    assert isinstance(t1, StoreValue)
    assert isinstance(t2, StoreValue)
    assert isinstance(t3, StoreValue)
    assert isinstance(t4, StoreValue)

    print("\n---TEST: Ensure custom Value has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    d3 = t3.get_default()
    d4 = t4.get_default()
    # print (d1)
    # print (d2)
    # print (d3)
    # print (d4)
    assert d1 == UNSET
    assert d2 == "ARG_DEFAULT_OVERRIDE"
    assert d3 == "DEFAULT_FROM_VALUE_CLASS 4444"
    assert d4 == "ARG_DEFAULT_OVERRIDE"


def test2():
    # ValueDict level testing

    # Test Core ValueDict
    # ===========================
    cd1 = {"default_item": "CLASS_DEFAULT_OVERRIDE"}
    cd2 = {"default_item_from_args": "ARG_DEFAULT_OVERRIDE"}

    print("\n\n===> Test core ValueDict <====\n\n")

    class TestConfig1(Configuration):
        dict_lib_undefaulted = ValueDict()
        dict_lib_undefaulted_via_args = ValueDict(default=cd1)

    p1 = TestConfig1()

    print("\n---TEST: Ensure core ValueDict are correct type")
    t1 = p1["dict_lib_undefaulted"]
    t2 = p1["dict_lib_undefaulted_via_args"]
    assert isinstance(t1, StoreValue)
    assert isinstance(t2, StoreValue)

    print("\n---TEST: Ensure core ValueDict has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    # print (d1)
    # print (d2)
    assert d1 == {}
    assert d2 == cd1

    # Test Custom  ValueDict
    # ===========================

    print("\n\n===> Test custom ValueDict <====\n\n")

    class ValueUnDefaulted(ValueDict):
        "Simple var wihtout defaults"

    class ValueDefaulted(ValueDict):
        "Simple var with default"

        # Old way
        # _default = cd1
        # New way
        class Meta:
            default = cd1

    class TestConfig1(Configuration):
        val_lib_undefaulted = ValueUnDefaulted()
        val_lib_undefaulted_via_args = ValueUnDefaulted(default=cd2)

        val_lib_defaulted = ValueDefaulted()
        val_lib_defaulted_via_args = ValueDefaulted(default=cd2)

    p1 = TestConfig1()

    print("\n---TEST: Ensure custom ValueDict are correct type")
    t1 = p1["val_lib_undefaulted"]
    t2 = p1["val_lib_undefaulted_via_args"]
    t3 = p1["val_lib_defaulted"]
    t4 = p1["val_lib_defaulted_via_args"]
    assert isinstance(t1, StoreDict)
    assert isinstance(t2, StoreDict)
    assert isinstance(t3, StoreDict)
    assert isinstance(t4, StoreDict)

    print("\n---TEST: Ensure custom ValueDict has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    d3 = t3.get_default()
    d4 = t4.get_default()
    # print (d1)
    # print (d2)
    # print (d3)
    # print (d4)
    assert d1 == {}
    assert d2 == cd2
    assert d3 == cd1
    assert d4 == cd2


def test3():
    # ValueConf level testing

    # Test Core ValueConf
    # ===========================
    cd1 = {"default_item": "CLASS_DEFAULT_OVERRIDE"}
    cd2 = {"default_item_from_args": "ARG_DEFAULT_OVERRIDE"}

    print("\n\n===> Test core ValueConf <====\n\n")

    class TestConfig1(Configuration):
        dict_lib_undefaulted = ValueConf()
        dict_lib_undefaulted_via_args = ValueConf(default=cd1)

    p1 = TestConfig1()

    print("\n---TEST: Ensure core ValueConf are correct type")
    t1 = p1["dict_lib_undefaulted"]
    t2 = p1["dict_lib_undefaulted_via_args"]
    assert isinstance(t1, StoreValue)
    assert isinstance(t2, StoreValue)

    print("\n---TEST: Ensure core ValueConf has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    print(d1)
    print(d2)
    assert d1 == {}
    assert d2 == cd1

    # Test Custom  ValueConf
    # ===========================

    print("\n\n===> Test custom ValueConf <====\n\n")

    class ValueUnDefaulted(ValueConf):
        "Simple var wihtout defaults"

    class ValueDefaulted(ValueConf):
        "Simple var with default"

        class Meta:
            default = cd1

    class TestConfig1(Configuration):
        val_lib_undefaulted = ValueUnDefaulted()
        val_lib_undefaulted_via_args = ValueUnDefaulted(default=cd2)
        val_lib_defaulted = ValueDefaulted()
        val_lib_defaulted_via_args = ValueDefaulted(default=cd2)

    p1 = TestConfig1()

    print("\n---TEST: Ensure custom ValueDict are correct type")
    t1 = p1["val_lib_undefaulted"]
    t2 = p1["val_lib_undefaulted_via_args"]
    t3 = p1["val_lib_defaulted"]
    t4 = p1["val_lib_defaulted_via_args"]
    assert isinstance(t1, StoreDict)
    assert isinstance(t2, StoreDict)
    assert isinstance(t3, StoreDict)
    assert isinstance(t4, StoreDict)

    print("\n---TEST: Ensure custom ValueDict has correct defaults")
    d1 = t1.get_default()
    d2 = t2.get_default()
    d3 = t3.get_default()
    d4 = t4.get_default()
    # print (d1)
    # print (d2)
    # print (d3)
    # print (d4)
    assert d1 == {}
    assert d2 == cd2
    assert d3 == cd1
    assert d4 == cd2


test1()
test2()
test3()
