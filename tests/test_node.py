import pytest
import inspect
from logging import Logger
from pprint import pprint

# from classyconf.casts import Boolean, List, Option, Tuple, evaluate
# from classyconf.exceptions import InvalidConfiguration

from superconf.node import NodeBase, NodeContainer, NodeMeta, NodeChildren
from superconf.node import UNSET, DEFAULT_VALUE, UNSET_VALUE
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
    assert inst.fname == ""


def test_node_cls_base_args():
    "Test with overrides"

    inst1 = NodeBase(name="My Parent")
    inst2 = NodeBase(name="My Child", parent=inst1)

    assert inst1.name == "My Parent"
    assert inst1.parent == None
    assert inst1.fname == "My Parent"
    assert inst2.name == "My Child"
    assert inst2.parent == inst1
    assert inst2.fname == "My Parent.My Child"


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

    # Test get_parents, mode=invalid
    try:
        p1.get_parents(mode="invalid")
        assert False
    except Exception:
        pass

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

    # # Test get_parents, mode=self
    # assert p1.get_parents(mode="self") == p1
    # assert p2.get_parents(mode="self") == p2
    # assert c1.get_parents(mode="self") == c1
    # assert c2.get_parents(mode="self") == c2
    # assert c3.get_parents(mode="self") == c3
    # assert c4.get_parents(mode="self") == c4


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

    # Try to re add and re-add child
    p2.add_child(c6)
    try:
        p2.add_child(c6)
        assert False
    except Exception:
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

    # Test children direct access
    assert p1.get_children("My Child1") == c1
    assert p1.get_children("My Child2") == c2
    assert p2.get_children("My Sub Child4") == c4
    assert p2.get_children("My Sub Child6") == c6

    # Test on missing children
    assert p2.get_children("UNEXISTING CHILD") == None

    # Try to replace child
    c6b = NodeContainer(name="My Sub Child6", logger_prefix="TEST_PREFIX")
    u1 = p2.get_children("My Sub Child6")
    p2.add_child(c6b)
    u2 = p2.get_children("My Sub Child6")

    pprint(u1.__dict__)
    pprint(u2.__dict__)

    assert u1 != u2
    assert u1._logger_prefix != u2._logger_prefix

    # Try to update child

    # assert u1.get_default()
    # assert u2.get_default() == "NEW DEFAULTS"


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

    # Test class mode
    logger_mode = "class"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)

    assert isinstance(inst1.log, Logger)
    assert inst1.log.name == "superconf.node.NodeContainer"
    assert inst2.log.name == "superconf.node.NodeContainer"

    # Test invalid mode
    logger_mode = "invalid"
    try:
        inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
        assert False
    except Exception:
        pass
    try:
        inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)
        assert False
    except Exception:
        pass

    # assert isinstance(inst1.log, Logger)
    # assert inst1.log.name == "superconf.node.NodeContainer.My Parent"
    # assert inst2.log.name == "superconf.node.NodeContainer.My Child"


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

    # Test inheritance 3 - use case 3
    logger_mode = "inherit"
    inst1 = NodeContainer(name="My Parent", logger_mode=logger_mode)
    inst2 = NodeContainer(name="My Child", logger_mode=logger_mode, parent=inst1)

    assert hasattr(inst1, "log")
    assert hasattr(inst2, "log")
    assert isinstance(inst1.log, Logger)
    assert isinstance(inst2.log, Logger)
    assert inst1.log == inst1.log


# ================================================
# Tests Node helpers
# ================================================


def test_nodecont_helpers():
    "Test helper modes"

    t1 = DEFAULT_VALUE
    assert str(t1) == "<DEFAULT_VALUE>"

    t1 = UNSET_VALUE
    assert str(t1) == "<UNSET_VALUE>"


# ================================================
# Tests Class: NodeMeta
# ================================================


def test_nodemeta_cls_default():
    "Test a default NodeBase"

    inst = NodeMeta()

    assert inspect.isclass(NodeMeta.Meta)
    assert inspect.isclass(inst.Meta)

    t1 = inst.get_inst_cfg("value_missing")
    assert t1 == UNSET

    t1 = inst.get_inst_cfg("value_missing", default="MISSING")
    assert t1 == "MISSING"


def test_nodemeta_get_config():
    "Test a default NodeBase"

    class TestClass(NodeMeta):

        _value2 = "fromInternalOverride"
        value3 = "fromClass"

        class Meta:
            value1 = "fromMetaValue"

    inst = TestClass()

    # Test scnearios
    t1 = inst.get_inst_cfg("value1")
    assert t1 == "fromMetaValue"

    t1 = inst.get_inst_cfg("value2")
    assert t1 == "fromInternalOverride"

    t1 = inst.get_inst_cfg("value3")
    assert t1 == "fromClass"


# ================================================
# Tests Class: NodeChildren
# ================================================


# def test_nodechildren_cls_default():
#     "Test a default NodeBase"

#     inst = NodeChildren()

#     assert inspect.isclass(NodeMeta.Meta)
#     assert inspect.isclass(inst.Meta)


#     t1 = inst.get_inst_cfg("value_missing")
#     assert t1 == UNSET

#     t1 = inst.get_inst_cfg("value_missing", default="MISSING")
#     assert t1 == "MISSING"
