
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


class Stack(Configuration):

    path = Value(default="my_stack_path")
    name = Value(default="my_stack_name")


class PrjConfig(Configuration):

    prj_dir = Value()
    prj_namespace = Value(default="NO_NS")


class Project(Configuration):

    class Meta:
        loaders=[]
        additional_values = False

    simple1 = Value(default="UNSETTTT")
    simple2 = Value(default="UNSETTTT_FROM_CODE")
    never_set = Value(default="NEVERSET_FROM_CODE")


    # config1 = Value(default="UNSETTTT")
    # config2 = Value(default="UNSETTTT_FROM_CODE")



    # EX1: Nested declaration
    nested1 = ValueConf(
        item_class=PrjConfig,
    )
    nested2 = ValueConf(
        item_class=PrjConfig,
        default={"prj_dir": "DEFAULT_OVERRIDE"},
    )

    # config2 = ValueDict()

    # # EX1: Explicit declaration
    # stacks_list1 = ValueConf(
    #     child=StackList,
    # )
    # stacks_list2 = ValueList(
    #     children=Stack,
    # )
    # stacks_dict1 = ValueConf(
    #     child=StackDict,
    # )
    # stacks_dict2 = ValueDict(
    #     children=Stack,
    # )



    # # EX2: Container declaration
    # stacks_list_direct = ValueDict(
    #     children=Stack, # Must be existing Configuration
    # )

    # stacks = stacks_list_explicit


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


    config1 = Project(
        loaders=[
            YamlFile("paasify.yml"),
        ])

    config2 = Project(
        loaders=[
            YamlFile("paasify.yml"),
        ])

    print ("\n\n===> Test suite: TEst2 <====\n\n")


    # Test naming
    # ===========================

    print("\n---TEST: Instance names")
    config2 = Project(
        name = "MyRoot",
        loaders=[
            YamlFile("paasify.yml"),
        ])
    
    # config2.explain()
    assert config2.name == "MyRoot"


    # Test double instances
    # ===========================


    print("\n---TEST: Double instances - check same declared values")
    t1 = config1._declared_values
    t2 = config2._declared_values
    # pprint (t1)
    # pprint (t2)
    # pprint (id(t1))
    # pprint (id(t2))
    assert id(t1) == id(t2)
    for key, val in t1.items():
        assert val == t2[key]
    assert t1 == t2
    assert t1 is t2


    print("\n---TEST: Double instances - check different children instances")
    t1 = config1._children
    t2 = config2._children
    pprint (config1.__dict__)
    pprint (config2.__dict__)
    pprint (t1)
    pprint (t2)
    pprint (id(t1))
    pprint (id(t2))
    assert id(t1) != id(t2)
    for key, val in t1.items():
        assert val != t2[key]
    # assert t1 == {}
    # assert t2 == {}
    assert t1 is not t2


    # Test get_hier
    # ===========================

    print("\n---TEST: Test hier - full")
    t = config1.get_hier(mode="full")
    # pprint (t)
    assert t == [config1]

    print("\n---TEST: Test hier - parents")
    t = config1.get_hier(mode="parents")
    # pprint (t)
    assert t == []


    print("\n---TEST: Test hier - first")
    t = config1.get_hier(mode="first")
    # pprint (t)
    assert t == None

    print("\n---TEST: Test hier - self")
    t = config1.get_hier(mode="self")
    # pprint (t)
    assert t is config1


    print("\n---TEST: Test hier - root")
    t = config1.get_hier(mode="root")
    # pprint (t)
    assert t is config1


    # Test get_children
    # ===========================

    print("\n---TEST: Test get_children - full")
    t = config1.get_children()
    # pprint (t)
    assert isinstance(t, dict)
    for key, val in t.items():
        assert isinstance(val, StoreValue)


    # Test dump_tree
    # ===========================

    print("\n---TEST: Test dump_tree")
    t = config1.explain()
    # pprint (config1.__dict__)
    # pprint (t)
    # assert isinstance(t, dict)
    # for key, val in t.items():
    #     assert isinstance(val, StoreValue)



    # Test dunders
    # ===========================

    # __iter__
    print("\n---TEST: Test iteration - __iter__")
    for target in [config1, config1["nested1"]]:
        # print (f"Child key of: {target}")
        count = 0
        for x in target:
            # print ( "  - ", x)
            count = count +1
        assert count > 1, "I should have at least one child in each node"
        print (f"  - Count {target}: {count}")

    # __contains__
    print("\n---TEST: Child existance by key - __contains__")
    assert "nested1" in config1
    assert "nested2" in config1
    assert "nested0" not in config1


    # __getitem__

    print("\n---TEST: Test dunders access - (value)")
    t1 = config1["simple1"]
    # pprint (t1)
    t2 = config1["simple1"]
    t3 = config1["simple2"]
    # pprint (t2)
    # pprint (t3)
    assert t1 == t2
    assert t1 != t3
    assert isinstance(t1, StoreValue)

    print("\n---TEST: Test dunders access - nested - L1 (object)")
    t1 = config1["nested1"]
    # pprint (t1)
    t2 = config1["nested1"]
    t3 = config1["nested2"]
    # pprint (t2)
    # pprint (t3)
    assert t1 == t2
    assert t1 != t3
    assert isinstance(t1, StoreDict)


    print("\n---TEST: Test dunders access - nested - L2/* (value)")
    t1 = config1["nested1"]["prj_dir"]
    # pprint (t1)
    t2 = config1["nested1"]["prj_dir"]
    t3 = config1["nested2"]["prj_dir"]
    # pprint (t2)
    # pprint (t3)
    
    assert t1 == t2
    assert t1 != t3
    assert isinstance(t1, StoreValue)

    t4 = config1["nested1"]["prj_namespace"]
    t5 = config1["nested2"]["prj_namespace"]
    assert t4 != t5
    assert isinstance(t4, StoreValue)





    # Test default value access
    # ===========================

    t1 = config1["nested2"]
    t2 = config1["nested2"]["prj_dir"]
    t3 = config1["nested1"]["prj_dir"]

    # print ("t1 VALUE =", t1.get_value())
    # print ("t2 VALUE =", t2.get_value())
    # print ("t3 VALUE =", t3.get_value())

    assert t2.get_value() == "DEFAULT_OVERRIDE"
    

    # pprint(t3.__dict__)
    # print("default should be NOT_SET")
    # pprint(config1["nested1"]._default)
    # pprint(config1["nested1"]["prj_dir"]._default)
    assert t3.get_value() == UNSET
    # assert False, "SUCCESS"




def test2():
    # Second level testing


    # Init objects
    # ===========================
    config1 = Project(
        loaders=[
            YamlFile("paasify.yml"),
        ])


    # TEsts
    # ===========================
    print ("\n\n===> Test suite: TEst2 <====\n\n")

    print("\n---TEST: Test Key metas attributes")

    t0 = config1
    t1 = config1["nested1"]
    t2 = config1["nested1"]["prj_dir"]
    t3 = config1["nested1"]["prj_namespace"]

    t0.explain()
    t1.explain()
    t2.explain()
    t3.explain()

    print ("--- print() -- MUST BE LISIBLE")
    print ("t0:", t0)
    print ("t1:", t1)
    print ("t2:", t2)
    print ("t3:", t3)

    print ("--- __str__() -- MUST BE LISIBLE")
    print ("t0:", str(t0))
    print ("t1:", str(t1))
    print ("t2:", str(t2))
    print ("t3:", str(t3))

    print ("--- __repr__() -- MUST BE UNAMBIGOUS")
    print ("t0:", repr(t0))
    print ("t1:", repr(t1))
    print ("t2:", repr(t2))
    print ("t3:", repr(t3))


    print ("--- .name")
    print ("t0:", t0.name)
    print ("t1:", t1.name)
    print ("t2:", t2.name)
    print ("t3:", t3.name)

    print ("--- .fname")
    print ("t0:", t0.fname)
    print ("t1:", t1.fname)
    print ("t2:", t2.fname)
    print ("t3:", t3.fname)


    print ("--- .key")
    print ("t0:", t0.key)
    print ("t1:", t1.key)
    print ("t2:", t2.key)
    print ("t3:", t3.key)
    assert t0.key == ""
    assert t1.key == "nested1"
    assert t2.key == "prj_dir"
    assert t3.key == "prj_namespace"

    print ("--- .get_value()")    
    print ("t0:", t0.get_value())
    print ("t1:", t1.get_value())
    print ("t2:", t2.get_value())
    print ("t3:", t3.get_value())
    assert isinstance(t0.get_value(), dict) 
    assert isinstance(t1.get_value(), dict)
    assert isinstance(t2.get_value(), type(UNSET)) 
    assert isinstance(t3.get_value(), str) 

    print ("--- .get_key(parents)")
    print ("t0:", t0.get_key(mode="full"))
    print ("t1:", t1.get_key(mode="full"))
    print ("t2:", t2.get_key(mode="full"))
    print ("t3:", t3.get_key(mode="full"))
    assert len(t0.get_key(mode="full")) == 1
    assert len(t1.get_key(mode="full")) == 2
    assert len(t2.get_key(mode="full")) == 3
    assert len(t3.get_key(mode="full")) == 3

    print ("--- .get_key(full)")
    print ("t0:", t0.get_key(mode="parents"))
    print ("t1:", t1.get_key(mode="parents"))
    print ("t2:", t2.get_key(mode="parents"))
    print ("t3:", t3.get_key(mode="parents"))
    assert t0.get_key(mode="parents").count('.') == 0
    assert t1.get_key(mode="parents").count('.') == 1
    assert t2.get_key(mode="parents").count('.') == 2
    assert t3.get_key(mode="parents").count('.') == 2

    print ("--- .get_key(children)") 
    print ("t0:", t0.get_key(mode="children"))
    print ("t1:", t1.get_key(mode="children"))
    print ("t2:", t2.get_key(mode="children"))
    print ("t3:", t3.get_key(mode="children"))
    assert len(t1.get_key(mode="children")) == 2
    assert len(t2.get_key(mode="children")) == 0
    assert len(t3.get_key(mode="children")) == 0





logging.basicConfig(level="DEBUG")


test1()
test2()
# test3()
