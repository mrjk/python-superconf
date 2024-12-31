
import logging
from pprint import pprint
import argparse

from superconf.loaders import YamlFile, UNSET, NOT_SET

from superconf.configuration import Configuration, ConfigurationDict, ConfigurationList
from superconf.configuration import ValueConf, ValueDict, ValueList, Value
from superconf.configuration import StoreValue, StoreDict, StoreList

parser = argparse.ArgumentParser(description='Does something useful.')
parser.add_argument('--debug', '-d', dest='debug', default=NOT_SET, help='set debug mode')
args = parser.parse_args()




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


class PrjConfig(Configuration):

    prj_dir = Value()
    prj_namespace = Value(default="NO_NS")

class PrjRuntime(Configuration):
    "Stack runtime"

    always_build = Value(default=True)


class Project(Configuration):

    class Meta:
        loaders=[]
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


import json

def dump_json(obj):
    "Return a node object to serializable thing"

    def t_funct(item):

        if item is UNSET:
            return None
        if hasattr(item, "get_value"):
            return item.get_value()
        raise Exception(f"Unparseable item: {item}")


    return json.dumps(obj, 
        indent=2,
        default=t_funct,
        )


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
        }
    }

    p1 = Project(
        value = dict(c1),
        name = "MYAPP",
        loaders=[
            YamlFile("paasify.yml"),
        ])

    print ("\n\n===> Test suite: TEst1 App <====\n\n")


    p1.explain()


    print ("\n\n===> Test get all children keys <====\n\n")

    o1 = p1.flatify_children(mode="all")
    o2 = p1.flatify_children(mode="containers")
    o3 = p1.flatify_children(mode="keys")
    # pprint (o1)
    # pprint (o2)
    # pprint (o3)

    assert len(o2) != 0
    for i in o1:
        assert (i in o2) or (i in o3), f"Missing: {i}"
    assert len (o1) == (len(o2) + len(o3))



    print ("\n\n===> Test dump keys <====\n\n")
    o1 = p1.dump_keys(mode="all")
    o2 = p1.dump_keys(mode="containers")
    o3 = p1.dump_keys(mode="keys")
    pprint (o1)
    pprint (o2)
    pprint (o3)

    assert len(o2) != 0
    for i, val in o1.items():
        assert (i in o2) or (i in o3), f"Missing: {i}"
    for i, val in o1.items():
        assert (i in o2) or (i in o3), f"Missing: {i}"



    print ("\n\n===> Test get_env_vars <====\n\n")
    o1 = p1.get_envvars(mode="all")
    o2 = p1.get_envvars(mode="containers")
    o3 = p1.get_envvars(mode="keys")
    # # pprint (o1)
    # # pprint (o2)
    pprint (o3)
    for key, child in o1.items():
        assert key.startswith("MYAPP")




    # o1 = p1.get_envvar_name(mode="all")
    # pprint(o1)

    return

    assert False, "WIPP ENV VARS"

    # t = p1.explain_tree(mode="struct")
    # print (dump_json(t))



    t = p1.explain_tree(mode="struct", lvl=2)
    print (dump_json(t))
    t = p1.explain_tree(mode="struct", lvl=1)
    print (dump_json(t))
    t = p1.explain_tree(mode="struct", lvl=0)
    print (dump_json(t))
    t = p1.explain_tree(mode="struct", lvl=-1)
    print (dump_json(t))


    t = p1.explain_tree()
    print (dump_json(t))
    t = p1.explain_tree(lvl=1)
    print (dump_json(t))


    print ("____________________")
    # t = p1.dump_keys()
    # pprint (t)

    return

    return


    print ("get default:")
    pprint (p1.get_default())
    print ("get value:")
    pprint (p1.get_value())
    return


    # Test Explicit - with data and children
    # ===========================

    print("\n---TEST: Explicit Dict - Create new config with Feed value")
    c1 = {
        "stacks_dict1": {
            "stack1": {},
            "stack2": {},
        }
    }
    p1 = Project(
        loaders=[],
        value = dict(c1)
        )
    p1.explain()
    p1["stacks_dict1"].explain()
    pprint (p1._value)
    assert p1._value == c1
    # assert False
    # assert False

    print("\n---TEST: Explicit Dict - Create new config with Feed default")
    p1 = Project(
        loaders=[],
        default = dict(c1)
        )
    p1.explain()
    p1["stacks_dict1"].explain()



    print("\n---TEST: Explicit Dict - Create new orphan stack child with values")
    child1 = Stack(
        key="stack3",
        value={
            "path": "New_path3",
            "name": "New_name3",
        },
    )
    child1.explain()


    # assert False, "CHECK defaults and values"

    print("\n---TEST: Explicit Dict - Add stack child in live")
    curr_child = 2  # Added from previously added child
    assert len(p1["stacks_dict1"]._children) == (0 + curr_child)
    p1["stacks_dict1"].add_child(child1)
    assert len(p1["stacks_dict1"]._children) == (1 + curr_child)

    # Ensure child is the same
    assert "stack3" in p1["stacks_dict1"]
    assert child1 == p1["stacks_dict1"]["stack3"]
    assert child1 is p1["stacks_dict1"]["stack3"]

    # print ("====")
    # p1["stacks_dict1"]["stack3"].explain()
    p1["stacks_dict1"].explain()
    child1.explain()
    # print ("====")



    # Test Implicit Dict - with data and children
    # ===========================

    print("\n---TEST: Implicit Dict - Create new config with Feed value")
    c1 = {
        "stacks_dict1": {
            "stack1": {
                "prj_dir": "tutu1"
            },
            "stack2": {},
        },
        "stacks_dict2": {
            "stack1": {
                "prj_dir": "tutu2"
            },
            "stack2": {},
        }

    }
    p1 = Project(
        loaders=[],
        value = dict(c1)
        )
    p1.explain()
    print ("===== COMPARE")
    p1["stacks_dict1"].explain()
    p1["stacks_dict2"].explain()


    pprint (p1._value)
    assert p1._value == c1
    # assert False
    # assert False



test1()
# test2()
