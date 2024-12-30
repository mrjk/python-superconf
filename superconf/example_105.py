

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




# Example structure 1

class Stack(Configuration):

    path = Value(default="my_stack_path")
    name = Value(default="my_stack_name")


class StacksDict(ConfigurationDict):
    "Dict of stacks"

    class Meta:
        item_class = Stack

class StacksList(ConfigurationList):
    "List of stacks"

    class Meta:
        item_class = Stack


class PrjConfig(Configuration):

    prj_dir = Value()
    prj_namespace = Value(default="NO_NS")


class Project(Configuration):

    class Meta:
        loaders=[]
        additional_values = False

    # EX2: Explicit subdict
    stacks_dict1 = ValueConf(
        item_class=StacksDict,
    )
    stacks_dict2 = ValueDict(
        item_class=Stack,
    )


    # EX3: Explicit declaration
    stacks_list1 = ValueConf(
        item_class=StacksList,
    )
    stacks_list2 = ValueList(
        item_class=Stack,
    )
    


logging.basicConfig(level="DEBUG")

exemple_conf0 = {}

exemple_conf1 = {
    "simple1": "strgni_from dict",
    "simple2": "string from dict",
    # "": "",
    # "": "",
}

#########


def test1():
    # First level testing


    # Init objects
    # ===========================
    p2 = Project(
        loaders=[
            YamlFile("paasify.yml"),
        ])

    print ("\n\n===> Test suite: TEst1 Dict <====\n\n")


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



def test2():


    # Init objects
    # ===========================
    p2 = Project(
        loaders=[
            YamlFile("paasify.yml"),
        ])

    print ("\n\n===> Test suite: TEst2 - List <====\n\n")


    # Test Explicit - with data and children
    # ===========================

    c1 = {
        "stacks_list1": [
            {
                "name": "hardcoded",
                "prj_dir": "tutu1"
            },
            {},
        ],
        "stacks_list2": [
            {
                "prj_dir": "tutu2"
            },
            {},
        ]
    }

    print("\n---TEST: Explicit List - Create new config with Feed default")
    p1 = Project(
        loaders=[],
        default = dict(c1)
        )
    p1.explain()
    p1["stacks_list1"].explain()


    print("\n---TEST: Explicit List - Create new config with Feed value")
    p1 = Project(
        loaders=[],
        value = dict(c1)
        )
    p1.explain()
    p1["stacks_list1"].explain()
    pprint (p1._value)
    assert p1._value == c1
    # assert False
    # assert False



    print("\n---TEST: Explicit List - Create new orphan stack child with values")
    child1 = Stack(
        key="stack3",
        value={
            "path": "New_path3",
            "name": "New_name3",
        },
    )
    child1.explain()


    print("\n---TEST: Explicit List - Add stack child in live")
    curr_child = 2  # Added from previously added child
    p1["stacks_list1"].explain()
    assert len(p1["stacks_list1"]._children) == (0 + curr_child)
    p1["stacks_list1"].add_child(child1)
    assert len(p1["stacks_list1"]._children) == (1 + curr_child)

    # Ensure child is the same
    assert "stack3" in p1["stacks_list1"]
    assert child1 == p1["stacks_list1"]["stack3"]
    assert child1 is p1["stacks_list1"]["stack3"]

    # print ("====")
    # p1["stacks_list1"]["stack3"].explain()
    p1["stacks_list1"].explain()
    child1.explain()
    # print ("====")



    # Test Implicit Dict - with data and children
    # ===========================

    print("\n---TEST: Implicit List - Create new config with Feed value")
    p1 = Project(
        loaders=[],
        value = dict(c1)
        )
    p1.explain()
    print ("===== COMPARE")
    p1["stacks_list1"].explain()
    p1["stacks_list2"].explain()


    pprint (p1._value)
    assert p1._value == c1
    # assert False
    # assert False






# def test3():
#     # Third level testing


#     # Init objects
#     # ===========================
#     c1 = {
#         "stacks_list1": [
#             {
#                 "name": "hardcoded",
#                 "prj_dir": "tutu1"
#             },
#             {},
#         ],
#         "stacks_list2": [
#             {
#                 "prj_dir": "tutu2"
#             },
#             {},
#         ]
#     }
#     root1 = Project(
#         default = dict(c1),
#         loaders=[
#             YamlFile("paasify.yml"),
#         ])


#     # Tests default and values
#     # ===========================
#     print ("\n\n===> Test suite: Test3 <====\n\n")

#     print("\n---TEST: Test inject with defaults")

#     root1.explain()

#     print ("FETCH DEFAULTS")
#     # print (type(root1.get_default()))
#     print (root1.get_default())

#     assert False



test1()
test2()
# test3()
