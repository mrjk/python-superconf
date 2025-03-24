"""Test suite for Node class base functionality."""

import pytest

from superconf.nodes import NOT_SET, Node


class TestNodeBase:
    """Test suite for basic Node functionality."""

    def test_11_direct_node_base(self):
        """Test basic Node instantiation and dunder methods."""
        # Context setup
        t = Node()

        # Test dunder methods presence and default values
        assert hasattr(t, "__node_key__")
        assert hasattr(t, "__node_parent__")
        assert hasattr(t, "__node_value__")
        assert t.__node_key__ is None
        assert t.__node_parent__ is None
        assert t.__node_value__ is NOT_SET

        # Test attribute access methods
        assert t.__node_key__ is None
        assert t.__node_name__ == Node.__name__
        assert t.__node_fname__ == Node.__name__
        assert isinstance(t.__node_fkey__, str)
        assert t.__node_fkey__ == ""

    def test_12_direct_node_values(self):
        """Test Node instantiation with different parameter combinations."""
        # Test with key only
        t1 = Node(key="test_key")
        assert t1.__node_key__ == "test_key"
        assert t1.__node_parent__ is None
        assert t1.__node_value__ is NOT_SET

        # Test with value only
        test_value = {"data": "test"}
        t2 = Node(value=test_value)
        assert t2.__node_key__ is None
        assert t2.__node_parent__ is None
        assert t2.__node_value__ == test_value

        # Test with parent only
        parent_node = Node()
        t3 = Node(parent=parent_node)
        assert t3.__node_key__ is None
        assert t3.__node_parent__ == parent_node
        assert t3.__node_value__ is NOT_SET

        # Test with all parameters
        t4 = Node(key="full_test", value={"full": "test"}, parent=parent_node)
        assert t4.__node_key__ == "full_test"
        assert t4.__node_parent__ == parent_node
        assert t4.__node_value__ == {"full": "test"}

    def test_13_node_configuration(self):
        """Test Node configuration with different meta configurations."""

        # Test classes with different meta configurations
        class NodeWithMeta(Node):
            class Meta:
                NAME1 = "test_meta"

        class NodeWithMetaAttr(Node):
            __meta__ = type("Meta", (), {"NAME2": "test_meta_attr"})

        class NodeWithMetaName(Node):
            meta__NAME2 = "test_direct_meta"

        class NodeWithInit(Node):
            def __init__(self):
                self._NAME3 = "test_init"

        # Test instances
        node1 = NodeWithMeta()
        node2 = NodeWithMetaAttr()
        node3 = NodeWithMetaName()
        node4 = NodeWithInit()

        # Test __node_get_self_config__ basic functionality
        assert node1.__node_get_self_config__("NAME1") == "test_meta"
        assert node2.__node_get_self_config__("NAME2") == "test_meta_attr"
        assert node3.__node_get_self_config__("NAME2") == "test_direct_meta"
        assert node4.__node_get_self_config__("NAME3") == "test_init"

        # Test __node_get_self_config__ with parameters
        assert node1.__node_get_self_config__("MISSING", default="default") == "default"
        assert (
            node2.__node_get_self_config__("NAME2", override={"NAME2": "override"})
            == "override"
        )

        # Test with report parameter
        report = []
        cfg_value = node1.__node_get_self_config__("NAME1", report=report)
        assert cfg_value == "test_meta"
        assert report == ["class_meta:Meta.NAME1"]


class TestNodeNested:
    """Test suite for nested Node functionality."""

    def test_21_direct_node_nested(self):
        """Test nested Node structures."""
        # Context setup
        t1 = Node(key="k1", value={"level": 1}, parent=None)
        t2 = Node(key="k2", value={"level": 2}, parent=t1)
        t3 = Node(key="k3", value={"level": 3}, parent=t2)

        # Test t1 attributes
        assert t1.__node_key__ == "k1"
        assert t1.__node_parent__ is None
        assert t1.__node_value__ == {"level": 1}

        # Test t2 attributes
        assert t2.__node_key__ == "k2"
        assert t2.__node_parent__ == t1
        assert t2.__node_value__ == {"level": 2}

        # Test t3 attributes
        assert t3.__node_key__ == "k3"
        assert t3.__node_parent__ == t2
        assert t3.__node_value__ == {"level": 3}

    def test_22_nested_node_configuration(self):
        """Test nested Node configuration inheritance."""

        class _Common(Node):
            meta__BASE_VALUE = "base"
            meta__COMMON_VALUE = "UNSET"
            meta__OVERRIDE_VALUE = "UNSET"
            meta__CHILD_VALUE = "UNSET"
            meta__GRAND_CHILD_VALUE = "UNSET"

        class BaseConfig(_Common):

            class Meta:
                BASE_VALUE = "override"
                OVERRIDE_VALUE = "base"

        class ChildConfig(_Common):
            class Meta:
                CHILD_VALUE = "child"
                OVERRIDE_VALUE = "child"

        class GrandChildConfig(_Common):
            class Meta:
                GRAND_CHILD_VALUE = "grandchild"
                OVERRIDE_VALUE = "grandchild"

        # Create nested structure
        base_node = BaseConfig(key="base")
        child_node = ChildConfig(key="child", parent=base_node)
        grand_child = GrandChildConfig(key="grandchild", parent=child_node)

        # Test value inheritance
        report = []

        assert base_node.__node_get_self_config__("BASE_VALUE") == "override"
        assert child_node.__node_get_self_config__("BASE_VALUE") == "base"
        assert grand_child.__node_get_self_config__("BASE_VALUE") == "base"

        assert base_node.__node_get_self_config__("CHILD_VALUE") == "UNSET"
        assert child_node.__node_get_self_config__("CHILD_VALUE") == "child"
        assert grand_child.__node_get_self_config__("CHILD_VALUE") == "UNSET"

        assert base_node.__node_get_self_config__("GRAND_CHILD_VALUE") == "UNSET"
        assert child_node.__node_get_self_config__("GRAND_CHILD_VALUE") == "UNSET"
        assert grand_child.__node_get_self_config__("GRAND_CHILD_VALUE") == "grandchild"

        assert base_node.__node_get_self_config__("OVERRIDE_VALUE") == "base"
        assert child_node.__node_get_self_config__("OVERRIDE_VALUE") == "child"
        assert grand_child.__node_get_self_config__("OVERRIDE_VALUE") == "grandchild"

        # Test with override
        assert (
            grand_child.__node_get_self_config__(
                "OVERRIDE_VALUE", override={"OVERRIDE_VALUE": "custom"}
            )
            == "custom"
        )

        # Test with unexisting value
        assert (
            grand_child.__node_get_self_config__("UNEXISTING_VALUE", default="default")
            == "default"
        )

        # Test with report
        report = []
        value = grand_child.__node_get_self_config__("OVERRIDE_VALUE", report=report)
        assert value == "grandchild"
        assert report == ["class_meta:Meta.OVERRIDE_VALUE"]


# if __name__ == '__main__':
#     pytest.main([__file__])
