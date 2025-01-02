import logging
from pprint import pprint
import argparse


from superconf.common import dict_to_json, UNSET, NOT_SET

from superconf.loaders import YamlFile

from superconf.configuration import StoreValue, StoreDict, StoreList
from superconf.configuration import DEFAULT_VALUE, UNSET_VALUE

# from superconf.mixin import StoreValueEnvVars
# StoreValue = type('StoreValue',(StoreValue, StoreValueEnvVars),{})

from superconf.configuration import Configuration, ConfigurationDict, ConfigurationList
from superconf.configuration import ValueConf, ValueDict, ValueList, Value


parser = argparse.ArgumentParser(description="Does something useful.")
parser.add_argument(
    "--debug", "-d", dest="debug", default=NOT_SET, help="set debug mode"
)
args = parser.parse_args()


# Example 1 - Dict
# ==============================


class Var(Value):
    "Simple var"

    class Meta:
        default = "MISSING_VALUE_1234"


class VarCtlDict(ConfigurationDict):
    "Var controller withtout default value"

    class Meta:
        item_class = Var
        default = {"placeholder": DEFAULT_VALUE}


class VarCtlList(ConfigurationList):
    "Var controller withtout default value"

    class Meta:
        item_class = Var
        default = [
            DEFAULT_VALUE,
            "String Value",
            None,
        ]


exemple_conf0 = {}
exemple_conf1 = {
    # "simple1": "strgni_from dict",
    # "simple2": "string from dict",
    # "": "",
    "var2": "YEAAAH",
    "var1": [
        {
            "name": "stack1",
            "dir": "stack1",
        },
        {},
        None,
    ],
    "var3": DEFAULT_VALUE,
    "var4": UNSET,
}

exemple_conf_list1 = [
    # "simple1": "strgni_from dict",
    # "simple2": "string from dict",
    # "": "",
    {"var2": "YEAAAH"},
    {
        "var1": [
            {
                "name": "stack1",
                "dir": "stack1",
            },
            {},
            None,
        ]
    },
    {"var3": DEFAULT_VALUE},
    {"var4": UNSET},
]


# Example 1 - Dict
# ==============================


def test1():

    print("\n\n===> Test suite List: Validate dict config <====\n\n")

    p1 = VarCtlDict(
        value=dict(exemple_conf1),
    )

    # p1.explain()
    # print(dict_to_json(p1.explain_tree()))
    # print(dict_to_json(p1.explain_tree(mode="struct")))

    assert isinstance(p1.get_value(), dict)
    assert isinstance(p1.explain_tree(), dict)
    assert len(p1) == 4
    assert p1["var1"].get_value() == exemple_conf1["var1"]
    assert p1["var2"].get_value() == "YEAAAH"


def test2():
    "Test default values"

    print("\n\n===> Test suite Dict: Validate default config <====\n\n")
    p1 = VarCtlDict()
    # p1.explain()
    # p1["placeholder"].explain()
    # print(dict_to_json(p1.explain_tree()))
    # print(dict_to_json(p1.explain_tree(mode="struct")))

    assert isinstance(p1.get_value(), dict)
    assert isinstance(p1.explain_tree(), dict)
    assert len(p1) == 1
    assert p1["placeholder"].get_value() == "MISSING_VALUE_1234"


# Example 2 - List
# ==============================


def test3():

    print("\n\n===> Test suite List: Validate dict config <====\n\n")

    conf = exemple_conf_list1
    p1 = VarCtlList(
        value=list(conf),
    )

    # p1.explain()
    # pprint (p1.get_value())
    # print(dict_to_json(p1.explain_tree()))
    # print(dict_to_json(p1.explain_tree(mode="struct")))

    assert isinstance(p1.get_value(), list)
    assert isinstance(p1.explain_tree(), dict)
    assert len(p1) == 4
    assert p1["2"].get_value() == conf[2]
    assert p1["3"].get_value() == conf[3]


def test4():

    print("\n\n===> Test suite List: Validate dict config <====\n\n")

    conf = exemple_conf_list1
    p1 = VarCtlList()

    # p1.explain()
    # pprint (p1.get_value())
    # print(dict_to_json(p1.explain_tree()))
    # print(dict_to_json(p1.explain_tree(mode="struct")))

    assert isinstance(p1.get_value(), list)
    assert isinstance(p1.explain_tree(), dict)
    assert len(p1) == 3
    assert p1["0"].get_value() == "MISSING_VALUE_1234"
    assert p1["1"].get_value() == "String Value"
    assert p1["2"].get_value() == None


test1()
test2()
test3()
test4()
