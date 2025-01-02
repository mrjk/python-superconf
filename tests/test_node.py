import pytest
from logging import Logger
from pprint import pprint

# from classyconf.casts import Boolean, List, Option, Tuple, evaluate
# from classyconf.exceptions import InvalidConfiguration

from superconf.node import NodeBase, NodeContainer
import superconf.exceptions


# ================================================
# Tests Class: NodeBase
# ================================================


def test_node_cls_default():
    "Test a default NodeBase"

    inst = NodeBase()

    assert isinstance(inst.name, str)
    assert inst.name == ""
    assert inst.parent == None


def test_node_cls_base_args():
    "Test with overrides"

    inst1 = NodeBase(name="My Parent")
    inst2 = NodeBase(name="My Child", parent=inst1)

    assert inst1.name == "My Parent"
    assert inst1.parent == None
    assert inst2.name == "My Child"
    assert inst2.parent == inst1


def test_nodecont_cls_parent_links():
    "Test parent modes"

    # Simple hierarchy
    p1 = NodeBase(name="My Parent")
    c1 = NodeBase(name="My Child1", parent=p1)
    c2 = NodeBase(name="My Child2", parent=p1)

    assert c1.parent is p1
    assert c2.parent is p1

    # Let's create another hier
    p2 = NodeBase(name="My Sub Parent", parent=c2)
    c3 = NodeBase(name="My Sub Child3", parent=p2)
    c4 = NodeBase(name="My Sub Child4", parent=p2)

    # Ensure parents are correctly setup
    assert c3.parent is p2
    assert c4.parent is p2
    assert p2.parent is c2

    # Test get_parents, mode=parent
    assert [x.name for x in p1.get_parents(mode="parents")] == []
    assert [x.name for x in p2.get_parents(mode="parents")] == [
        "My Child2",
        "My Parent",
    ]
    assert [x.name for x in c1.get_parents(mode="parents")] == ["My Parent"]
    assert [x.name for x in c2.get_parents(mode="parents")] == ["My Parent"]
    assert [x.name for x in c3.get_parents(mode="parents")] == [
        "My Sub Parent",
        "My Child2",
        "My Parent",
    ]
    assert [x.name for x in c4.get_parents(mode="parents")] == [
        "My Sub Parent",
        "My Child2",
        "My Parent",
    ]

    # Test get_parents, mode=full
    pprint([x.name for x in p2.get_parents(mode="full")])
    assert [x.name for x in p1.get_parents(mode="full")] == ["My Parent"]
    assert [x.name for x in p2.get_parents(mode="full")] == [
        "My Sub Parent",
        "My Child2",
        "My Parent",
    ]
    assert [x.name for x in c1.get_parents(mode="full")] == ["My Child1", "My Parent"]
    assert [x.name for x in c2.get_parents(mode="full")] == ["My Child2", "My Parent"]
    assert [x.name for x in c3.get_parents(mode="full")] == [
        "My Sub Child3",
        "My Sub Parent",
        "My Child2",
        "My Parent",
    ]
    assert [x.name for x in c4.get_parents(mode="full")] == [
        "My Sub Child4",
        "My Sub Parent",
        "My Child2",
        "My Parent",
    ]

    # Test get_parents, mode=root
    assert p1.get_parents(mode="root").name == "My Parent"
    assert p2.get_parents(mode="root").name == "My Parent"
    assert c1.get_parents(mode="root").name == "My Parent"
    assert c2.get_parents(mode="root").name == "My Parent"
    assert c3.get_parents(mode="root").name == "My Parent"
    assert c4.get_parents(mode="root").name == "My Parent"

    # Test get_parents, mode=first
    pprint(p2.get_parents(mode="first").name)
    assert p1.get_parents(mode="first") == None
    assert p2.get_parents(mode="first").name == "My Child2"
    assert c1.get_parents(mode="first").name == "My Parent"
    assert c2.get_parents(mode="first").name == "My Parent"
    assert c3.get_parents(mode="first").name == "My Sub Parent"
    assert c4.get_parents(mode="first").name == "My Sub Parent"


# ================================================
# Tests Class: NodeContainer - Hierarchy
# ================================================


def test_nodecont_cls_children_links():
    "Test children modes"

    # Simple hierarchy
    p1 = NodeContainer(name="My Parent")
    c1 = NodeContainer(name="My Child1")
    c2 = NodeContainer(name="My Child2")

    p1.add_child(c1)
    p1.add_child(c2)

    # pprint (p1.__dict__)
    # pprint (p1.get_children())

    assert len(p1.get_children()) == 2
    assert len(c1.get_children()) == 0
    assert len(c1.get_children()) == 0

    # Let's create another hier
    p2 = NodeContainer(name="My Sub Parent")
    c3 = NodeContainer(name="My Sub Child3")
    c4 = NodeContainer(name="My Sub Child4")
    c5 = NodeContainer(name="My Sub Child5")
    c6 = NodeContainer(name="My Sub Child6")

    # Add child
    p2.add_child(c3)
    p2.add_child(c4)
    p1.add_child(c5)
    c1.add_child(p2)

    # Check get children are empty
    assert sorted(list(p1.get_children().keys())) == [
        "My Child1",
        "My Child2",
        "My Sub Child5",
    ]
    assert sorted(list(p2.get_children().keys())) == ["My Sub Child3", "My Sub Child4"]
    assert sorted(list(c1.get_children().keys())) == ["My Sub Parent"]
    assert sorted(list(c2.get_children().keys())) == []
    assert sorted(list(c3.get_children().keys())) == []
    assert sorted(list(c4.get_children().keys())) == []

    # Try to re add child
    try:
        p2.add_child(c6)
        assert False
    except:
        pass

    # Test parent ship
    assert [x.name for x in p1.get_parents(mode="parents")] == []
    assert [x.name for x in p2.get_parents(mode="parents")] == [
        "My Child1",
        "My Parent",
    ]
    assert [x.name for x in c1.get_parents(mode="parents")] == ["My Parent"]
    assert [x.name for x in c2.get_parents(mode="parents")] == ["My Parent"]
    assert [x.name for x in c3.get_parents(mode="parents")] == [
        "My Sub Parent",
        "My Child1",
        "My Parent",
    ]
    assert [x.name for x in c4.get_parents(mode="parents")] == [
        "My Sub Parent",
        "My Child1",
        "My Parent",
    ]

    # pprint ()

    # assert False

    # # Check get children are empty
    # assert [x.name for x in p1.get_children()] == []
    # assert [x.name for x in p2.get_children()] == []
    # assert [x.name for x in c1.get_children()] == []
    # assert [x.name for x in c2.get_children()] == []
    # assert [x.name for x in c3.get_children()] == []
    # assert [x.name for x in c4.get_children()] == []


def test_nodecont_cls_children_vs_parents():
    "Test children modes"

    # Simple hierarchy
    p1 = NodeContainer(name="My Parent")
    c1 = NodeContainer(name="My Child1", parent=p1)
    c2 = NodeContainer(name="My Child2", parent=p1)

    # Let's create another hier
    p2 = NodeContainer(name="My Sub Parent", parent=c2)
    c3 = NodeContainer(name="My Sub Child3", parent=p2)
    c4 = NodeContainer(name="My Sub Child4", parent=p2)

    # Check get children are empty
    assert [x.name for x in p1.get_children()] == []
    assert [x.name for x in p2.get_children()] == []
    assert [x.name for x in c1.get_children()] == []
    assert [x.name for x in c2.get_children()] == []
    assert [x.name for x in c3.get_children()] == []
    assert [x.name for x in c4.get_children()] == []


# ================================================
# Tests Class: NodeContainer - Logging
# ================================================


def test_nodecont_cls_base_loggers():
    "Test logging modes"

    # No log attributes
    logger_mode = "absent"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)

    assert not hasattr(inst1, "log")
    assert not hasattr(inst2, "log")

    # Test default mode
    logger_mode = "default"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)

    assert isinstance(inst1.log, Logger)
    assert inst1.log is inst2.log
    assert inst1.log.name == "superconf.node"

    # Test instance mode
    logger_mode = "instance"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)

    assert isinstance(inst1.log, Logger)
    assert inst1.log.name == "superconf.node.NodeContainer.My Parent"
    assert inst2.log.name == "superconf.node.NodeContainer.My Child"


def test_nodecont_cls_base_loggers_conf_inheritance():
    "Test logging modes inheritance"

    # Test inheritance - use case 1
    logger_mode = "instance"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode="inherit", parent=inst1)
    assert isinstance(inst1.log, Logger)
    assert inst1.log.name == "superconf.node.NodeContainer.My Parent"
    assert inst2.log.name == "superconf.node.NodeContainer.My Child"

    # Test inheritance 2 - use case 2
    logger_mode = "instance"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode="absent", parent=inst1)
    assert isinstance(inst1.log, Logger)
    assert not hasattr(inst2, "log")

    # assert False, "WIPPP OKK"


#     assert inst1.name == "My Parent"
#     assert inst1.parent == None
#     assert inst2.name == "My Child"
#     assert inst2.parent == inst1
