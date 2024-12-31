import logging
from pprint import pprint
import argparse


from superconf.common import dict_to_json
from superconf.loaders import YamlFile, UNSET, NOT_SET

from superconf.configuration import StoreValue, StoreDict, StoreList

# from superconf.mixin import StoreValueEnvVars
# StoreValue = type('StoreValue',(StoreValue, StoreValueEnvVars),{})

from superconf.configuration import Configuration, ConfigurationDict, ConfigurationList
from superconf.configuration import ValueConf, ValueDict, ValueList, Value


parser = argparse.ArgumentParser(description="Does something useful.")
parser.add_argument(
    "--debug", "-d", dest="debug", default=NOT_SET, help="set debug mode"
)
args = parser.parse_args()


# Add Mixins to Configuration

# class StoreValue(StoreValue, StoreValueEnvVars):
#     pass

# p.__class__ = type('GentlePerson',(Person,Gentleman),{})


class Var(Value):
    "Simple var"

    # KEY = Value(default="NO_KEY")
    # VALUE = Value(default="NO_VALUE")


class VarCtl(ConfigurationDict):
    "Var controller"

    class Meta:
        item_class = Var


class StackTag(Configuration):

    tag_name = Value(default="NO_KEY")
    tag_config = Value(default="NO_VALUE")


class Stack(Configuration):

    path = Value(default="NO_PATH")
    name = Value(default="NO_NAME")

    vars = ValueConf(
        item_class=VarCtl,
    )
    tags = ValueList(
        item_class=StackTag,
    )


class StacksList(ConfigurationList):
    "List of stacks"

    class Meta:
        item_class = Stack
        env_prefix = "MYAPP_STACKS"


class PrjConfig(Configuration):

    prj_dir = Value()
    prj_namespace = Value(default="NO_NS")


class PrjRuntime(Configuration):
    "Stack runtime"

    class Meta:
        env_prefix = "MYAPP_RUNTIME"

    always_build = Value(default=True)


class Project(Configuration):

    class Meta:
        loaders = []
        additional_values = False

    status = Value(default="Undefined")

    runtime = ValueConf(
        item_class=PrjRuntime,
    )
    prj = ValueConf(
        item_class=PrjConfig,
    )

    vars = ValueConf(
        item_class=VarCtl,
        # default={},
    )
    stacks = ValueConf(
        item_class=StacksList,
    )


exemple_conf0 = {}

exemple_conf1 = {
    "simple1": "strgni_from dict",
    "simple2": "string from dict",
    # "": "",
    # "": "",
}

#########


logging.basicConfig(level="DEBUG")


# import json

# def dict_to_json(obj):
#     "Return a node object to serializable thing"

#     def t_funct(item):

#         if item is UNSET:
#             return None
#         if hasattr(item, "get_value"):
#             return item.get_value()
#         raise Exception(f"Unparseable item: {item}")


#     return json.dumps(obj,
#         indent=2,
#         default=t_funct,
#         )


def test1():
    # First level testing

    # Init objects
    # ===========================
    c1 = {
        "stacks": [
            {
                "prj_dir": "tutu1",
                # "vars":
            },
            {},
        ],
        "vars": {
            "var_name": "var_value",
        },
    }

    p1 = Project(
        value=dict(c1),
        name="MYAPP",
        loaders=[
            YamlFile("paasify.yml"),
        ],
    )

    print("\n\n===> Test suite: TEst1 App <====\n\n")

    p1.explain()
    print(dict_to_json(p1.explain_tree()))
    # print(p1.to_json())
    # assert False

    print("\n\n===> Test get all children keys in list <====\n\n")

    o1 = p1.get_children_stores(mode="all")
    o2 = p1.get_children_stores(mode="containers")
    o3 = p1.get_children_stores(mode="keys")
    # pprint (o1)
    # pprint (o2)
    # pprint (o3)
    assert len(o2) != 0
    for i in o1:
        assert (i in o2) or (i in o3), f"Missing: {i}"
    assert len(o1) == (len(o2) + len(o3))

    print("\n\n===> Test dump keys <====\n\n")
    o1 = p1.dump_keys(mode="all")
    o2 = p1.dump_keys(mode="containers")
    o3 = p1.dump_keys(mode="keys")
    pprint(o1)
    # pprint (o2)
    # pprint (o3)
    assert len(o2) != 0
    for i, val in o1.items():
        assert (i in o2) or (i in o3), f"Missing: {i}"
    for i, val in o1.items():
        assert (i in o2) or (i in o3), f"Missing: {i}"

    print("\n\n===> Test get_env_vars <====\n\n")
    o1 = p1.get_envvars(mode="all")
    o2 = p1.get_envvars(mode="containers")
    o3 = p1.get_envvars(mode="keys")
    # # pprint (o1)
    # # pprint (o2)
    pprint(o3)
    for key, child in o1.items():
        assert key.startswith("MYAPP")

    print("____________________")

    return


test1()
# test2()
