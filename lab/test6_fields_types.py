import sys
from pprint import pprint

import pytest

import superconf.exceptions
from superconf.common import DEFAULT, FAIL, NOT_SET
from superconf.configuration import (
    Configuration,
    ConfigurationDict,
    Environment,
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

# This test explore the nested use cases, WITH defaults


# Test extra Fields
# =============================

print("\n\n================ Boolean Fields ===========\n\n")


class AppBools(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

        # TODO
        allow_unset = True  # Always the case actually

    # is_enabled = FieldBool() # Enabled, this should fail !
    is_online = FieldBool(default=False)

    bool_test1 = FieldBool(default="y")
    bool_test2 = FieldBool(default="off")


app1 = AppBools()

EXPECTED = {"bool_test1": True, "bool_test2": False, "is_online": False}

pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields Strings
# =============================

print("\n\n================ String Fields ===========\n\n")


class AppStrings(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    # is_enabled = FieldBool() # Enabled, this should fail !
    # is_online = FieldBool(default=False)

    # bool_test1 = FieldBool(default="y")
    # bool_test2 = FieldBool(default="off")
    string_test1 = FieldString(default="my_string")
    string_test2 = FieldString(default=False)
    string_test3 = FieldString(default=None)
    string_test4 = FieldString(default=23)
    string_test5 = FieldString(default=0)
    string_test6 = FieldString(default={"key": "value"})
    string_test7 = FieldString(default=["item1", "item2"])


app1 = AppStrings()

EXPECTED = {
    "string_test1": "my_string",
    "string_test2": "False",
    "string_test3": "None",
    "string_test4": "23",
    "string_test5": "0",
    "string_test6": "{'key': 'value'}",
    "string_test7": "['item1', 'item2']",
}

pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields Strings
# =============================

print("\n\n================ Int Fields ===========\n\n")


class AppInt(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    int_test1 = FieldInt(default=-1)
    int_test2 = FieldInt(default=1)
    int_test3 = FieldInt(default=0)
    int_test4 = FieldInt(default=4268)
    int_test5 = FieldInt(default=0)
    int_test6 = FieldInt(default=False)
    int_test7 = FieldInt(default=True)
    int_test8 = FieldInt()

    # int_test6 = FieldInt(default={"key": "value"})
    # int_test7 = FieldInt(default=["item1", "item2"])


app1 = AppInt()

EXPECTED = {
    "int_test1": -1,
    "int_test2": 1,
    "int_test3": 0,
    "int_test4": 4268,
    "int_test5": 0,
    "int_test6": 0,
    "int_test7": 1,
    "int_test8": NOT_SET,
}

pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields Strings
# =============================

print("\n\n================ Option Fields ===========\n\n")

options1 = {
    "_default_": 56789,
    "yes": "do_this_yes",
    "no": "do_something_else",
}


class AppOption(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    int_test1 = FieldOption(options1, default="yes")
    int_test2 = FieldOption(options1, default="no")
    int_test3 = FieldOption(
        options1, default="I Dont'exist", default_option="_default_"
    )

    int_test4 = FieldOption(options1, default_option="_default_")
    int_test5 = FieldOption(options1, default="_default_")

    # int_test4 = FieldOption(options1, default="failure") # Fail on strict mode

    # This should fail !
    # int_test3 = FieldOption(options1, default="I Dont'exist", default_option=FAIL)
    # int_test4 = FieldOption(options1, default="I Dont'exist")


app1 = AppOption()

EXPECTED = {
    "int_test1": "do_this_yes",
    "int_test2": "do_something_else",
    "int_test3": 56789,
    "int_test4": 56789,
    "int_test5": 56789,
}


pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields List
# =============================

print("\n\n================ List Fields ===========\n\n")


class AppList(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    list_test1 = FieldList(default=[])
    list_test2 = FieldList(default=["item1", "item2", "item3"])
    list_test3 = FieldList(default=0)
    list_test4 = FieldList(default=None)
    list_test5 = FieldList(default="item26")
    list_test6 = FieldList(default="item27,item28,item29")
    list_test7 = FieldList()


app1 = AppList()

EXPECTED = {
    "list_test1": [],
    "list_test2": ["item1", "item2", "item3"],
    "list_test3": [],
    "list_test4": [],
    "list_test5": ["item26"],
    "list_test6": ["item27", "item28", "item29"],
    "list_test7": [],
}


pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields List
# =============================

print("\n\n================ Tuple Fields ===========\n\n")


class AppTuple(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    list_test1 = FieldTuple(default=[])
    list_test2 = FieldTuple(default=["item1", "item2", "item3"])
    list_test3 = FieldTuple(default=0)
    list_test4 = FieldTuple(default=None)
    list_test5 = FieldTuple(default="item26")
    list_test6 = FieldTuple(default="item27,item28,item29")
    list_test7 = FieldTuple()


app1 = AppTuple()

EXPECTED = {
    "list_test1": (),
    "list_test2": ("item1", "item2", "item3"),
    "list_test3": (),
    "list_test4": (),
    "list_test5": ("item26",),
    "list_test6": ("item27", "item28", "item29"),
    "list_test7": (),
}


pprint(app1.get_values())
assert app1.get_values() == EXPECTED


# Test extra Fields Dict
# =============================

print("\n\n================ Dict Fields ===========\n\n")


class AppDict(Configuration):
    "Tests types"

    class Meta:
        # Will fail on undefined casted values if true, alow NOT_SET
        strict_cast = True

    field_test1 = FieldDict(default={})
    field_test2 = FieldDict(default={"item1": "val1", "item2": "val2", "item3": "val3"})
    list_test3 = FieldDict()
    # list_test4 = FieldTuple(default=None)
    # list_test5 = FieldTuple(default="item26")
    # list_test6 = FieldTuple(default="item27,item28,item29")


app1 = AppDict()

EXPECTED = {
    "field_test1": {},
    "field_test2": {"item1": "val1", "item2": "val2", "item3": "val3"},
    "list_test3": {},
}


pprint(app1.get_values())
assert app1.get_values() == EXPECTED


print("All tests O WIPK")
