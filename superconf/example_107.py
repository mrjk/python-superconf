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

    class Meta:
        default = "UNSET Value"


class VarCtl(ConfigurationDict):
    "Var controller withtout default value"

    class Meta:
        item_class = Var


class VarCtlWithDefault(ConfigurationDict):
    "Var controller with a default value"

    class Meta:
        item_class = Var
        default = {
            "default_harcoded_META": "val1_META",
            "val2": None,
            "val3": {},
            "val4": UNSET,
        }


class StackTag(Configuration):

    tag_name = Value(default="NO_KEY")
    tag_config = Value(default="NO_VALUE")


class Stack(Configuration):

    class Meta:
        default = {
            "name": "ExampleStack",
            "path": "MyExamplePath",
        }

    path = Value(default="NO_PATH")
    name = Value(default="NO_NAME")

    vars = ValueConf(
        item_class=VarCtlWithDefault,
    )
    # tags = ValueList(
    #     item_class=StackTag,
    #     default=[{"always1": "value1", "always2": "value2", "always3": None, "always3": UNSET }]
    # )


class StacksList(ConfigurationList):
    "List of stacks"

    class Meta:
        item_class = Stack
        env_prefix = "MYAPP_STACKS"

        # default = [{}]


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
        default={"default_harcoded1": "val1"},
    )

    # Ex1: Test defaults overrides
    stacks = ValueConf(
        item_class=StacksList,
    )


exemple_conf0 = {}

exemple_conf1 = {
    # "simple1": "strgni_from dict",
    # "simple2": "string from dict",
    # "": "",
    "stacks": [
        {
            "name": "stack1",
            "dir": "stack1",
        },
        # {},
        # None,
    ],
}


def test1():
    # First level testing

    # Init objects
    # ===========================
    p1 = Project(
        value=dict(exemple_conf1),
        name="MYAPP",
        loaders=[
            YamlFile("paasify.yml"),
        ],
    )

    print("\n\n===> Test suite: TEst1 App <====\n\n")

    p1.explain()
    print(dict_to_json(p1.explain_tree()))
    print(dict_to_json(p1.explain_tree(mode="struct")))

    # p1["stacks"].explain()
    # p1["stacks"]["0"].explain()

    p1["stacks"]["0"]["vars"].explain()
    p1["stacks"]["0"]["vars"]["val4"].explain()

    # print(p1.to_json())
    # assert False
    return


test1()
