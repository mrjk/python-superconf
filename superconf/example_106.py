


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



def test1():
    # First level testing

    # Test Core Values
    # ===========================

    print ("\n\n===> Test core Value <====\n\n")
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
    print (d1)
    print (d2)
    assert d1 == UNSET
    assert d2 == "ARG_DEFAULT_OVERRIDE"



    # Test Custom Values
    # ===========================

    print ("\n\n===> Test custom Value <====\n\n")

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

    print ("\n\n===> Test core ValueDict <====\n\n")
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

    print ("\n\n===> Test custom ValueDict <====\n\n")

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

    print ("\n\n===> Test core ValueConf <====\n\n")
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
    print (d1)
    print (d2)
    assert d1 == {}
    assert d2 == cd1



    # Test Custom  ValueConf
    # ===========================

    print ("\n\n===> Test custom ValueConf <====\n\n")

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










#############



def testxx():

    # p2.explain()


    # Test Value defaults
    # ===========================

    
    # ---
    print("\n---TEST: Value defaults and overrides (Core)")
    # p2["val_lib_undefaulted"].explain()
    t = p2["val_lib_undefaulted"].get_default()
    assert t == UNSET

    # p2["val_lib_undefaulted_via_args"].explain()
    print ("   ====================")
    p2["val_lib_undefaulted_via_args"].explain()
    pprint (p2["val_lib_undefaulted_via_args"].__dict__)
    print ("   ====================")
    t = p2["val_lib_undefaulted_via_args"].get_default()
    pprint(t)
    assert t == "ARG_DEFAULT_OVERRIDE"


    # ---
    print("\n---TEST: Value defaults and overrides (Custom)")

    # p2["val_undefaulted"].explain()
    t = p2["val_undefaulted"].get_default()
    assert t == UNSET

    # p2["val_defaulted_via_cls"].explain()
    print ("++++++++++++++++++++++++++")
    t = p2["val_defaulted_via_cls"].get_default()
    print ("RET DEFAULT", t)
    pprint (p2["val_defaulted_via_cls"].__dict__)
    assert t == "DEFAULT_FROM_VALUE_CLASS"
    
    # p2["val_undefaulted_via_args"].explain()
    t = p2["val_undefaulted_via_args"].get_default()
    print("RET", t)
    assert t == "ARG_DEFAULT_OVERRIDE"
    
    # p2["val_defaulted_via_args"].explain()
    t = p2["val_defaulted_via_args"].get_default()
    assert t == "ARG_DEFAULT_OVERRIDE"
    

    # ---
    print("\n---TEST: Container No Defaults (Core)")
    t = p2["dict_lib_undefaulted"].get_default()
    pprint(t)
    assert t == {}

    t = p2["conf_lib_undefaulted"].get_default()
    assert t == {}

    t = p2["list_lib_undefaulted"].get_default()
    pprint (t)
    assert t == {}


    return

    # ---
    print("\n---TEST: Dict defaults and overrides (Custom)")

    t = p2["list_lib_undefaulted"].get_default()
    assert t == {}



    # Test Dict defaults
    # ===========================


    # Test Conf defaults
    # ===========================

    # Test List defaults
    # ===========================




    return


#     ########################

#     # Test Explicit - with data and children
#     # ===========================

#     print("\n---TEST: Explicit Dict - Create new config with Feed value")
#     c1 = {
#         "stacks_dict1": {
#             "stack1": {},
#             "stack2": {},
#         }
#     }
#     p1 = Project(
#         loaders=[],
#         value = dict(c1)
#         )
#     p1.explain()
#     p1["stacks_dict1"].explain()
#     pprint (p1._value)
#     assert p1._value == c1
#     # assert False
#     # assert False

#     print("\n---TEST: Explicit Dict - Create new config with Feed default")
#     p1 = Project(
#         loaders=[],
#         default = dict(c1)
#         )
#     p1.explain()
#     p1["stacks_dict1"].explain()



#     print("\n---TEST: Explicit Dict - Create new orphan stack child with values")
#     child1 = Stack(
#         key="stack3",
#         value={
#             "path": "New_path3",
#             "name": "New_name3",
#         },
#     )
#     child1.explain()


#     # assert False, "CHECK defaults and values"

#     print("\n---TEST: Explicit Dict - Add stack child in live")
#     curr_child = 2  # Added from previously added child
#     assert len(p1["stacks_dict1"]._children) == (0 + curr_child)
#     p1["stacks_dict1"].add_child(child1)
#     assert len(p1["stacks_dict1"]._children) == (1 + curr_child)

#     # Ensure child is the same
#     assert "stack3" in p1["stacks_dict1"]
#     assert child1 == p1["stacks_dict1"]["stack3"]
#     assert child1 is p1["stacks_dict1"]["stack3"]

#     # print ("====")
#     # p1["stacks_dict1"]["stack3"].explain()
#     p1["stacks_dict1"].explain()
#     child1.explain()
#     # print ("====")



#     # Test Implicit Dict - with data and children
#     # ===========================

#     print("\n---TEST: Implicit Dict - Create new config with Feed value")
#     c1 = {
#         "stacks_dict1": {
#             "stack1": {
#                 "prj_dir": "tutu1"
#             },
#             "stack2": {},
#         },
#         "stacks_dict2": {
#             "stack1": {
#                 "prj_dir": "tutu2"
#             },
#             "stack2": {},
#         }

#     }
#     p1 = Project(
#         loaders=[],
#         value = dict(c1)
#         )
#     p1.explain()
#     print ("===== COMPARE")
#     p1["stacks_dict1"].explain()
#     p1["stacks_dict2"].explain()


#     pprint (p1._value)
#     assert p1._value == c1
#     # assert False
#     # assert False



# def test2():


#     # Init objects
#     # ===========================
#     p2 = Project(
#         loaders=[
#             YamlFile("paasify.yml"),
#         ])

#     print ("\n\n===> Test suite: TEst2 - List <====\n\n")


#     # Test Explicit - with data and children
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

#     print("\n---TEST: Explicit List - Create new config with Feed default")
#     p1 = Project(
#         loaders=[],
#         default = dict(c1)
#         )
#     p1.explain()
#     p1["stacks_list1"].explain()


#     print("\n---TEST: Explicit List - Create new config with Feed value")
#     p1 = Project(
#         loaders=[],
#         value = dict(c1)
#         )
#     p1.explain()
#     p1["stacks_list1"].explain()
#     pprint (p1._value)
#     assert p1._value == c1
#     # assert False
#     # assert False



#     print("\n---TEST: Explicit List - Create new orphan stack child with values")
#     child1 = Stack(
#         key="stack3",
#         value={
#             "path": "New_path3",
#             "name": "New_name3",
#         },
#     )
#     child1.explain()


#     print("\n---TEST: Explicit List - Add stack child in live")
#     curr_child = 2  # Added from previously added child
#     p1["stacks_list1"].explain()
#     assert len(p1["stacks_list1"]._children) == (0 + curr_child)
#     p1["stacks_list1"].add_child(child1)
#     assert len(p1["stacks_list1"]._children) == (1 + curr_child)

#     # Ensure child is the same
#     assert "stack3" in p1["stacks_list1"]
#     assert child1 == p1["stacks_list1"]["stack3"]
#     assert child1 is p1["stacks_list1"]["stack3"]

#     # print ("====")
#     # p1["stacks_list1"]["stack3"].explain()
#     p1["stacks_list1"].explain()
#     child1.explain()
#     # print ("====")



#     # Test Implicit Dict - with data and children
#     # ===========================

#     print("\n---TEST: Implicit List - Create new config with Feed value")
#     p1 = Project(
#         loaders=[],
#         value = dict(c1)
#         )
#     p1.explain()
#     print ("===== COMPARE")
#     p1["stacks_list1"].explain()
#     p1["stacks_list2"].explain()


#     pprint (p1._value)
#     assert p1._value == c1
#     # assert False
#     # assert False






# # def test3():
# #     # Third level testing


# #     # Init objects
# #     # ===========================
# #     c1 = {
# #         "stacks_list1": [
# #             {
# #                 "name": "hardcoded",
# #                 "prj_dir": "tutu1"
# #             },
# #             {},
# #         ],
# #         "stacks_list2": [
# #             {
# #                 "prj_dir": "tutu2"
# #             },
# #             {},
# #         ]
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
test3()
