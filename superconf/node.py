import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .common import NOT_SET, UNSET


log = logging.getLogger(__name__)


# def filter_NOT_UNSET(array, only=None, key=None):
#     assert isinstance(array, list)
#     out = []
#     for item in array:
#         if item == NOT_SET:
#             continue
#         if item == UNSET:
#             continue
#         if only is not None:
#             if not isinstance(item, only):
#                 continue
#         if key is not None:
#             if not isinstance(item, dict):
#                 continue
#             if not key in item:
#                 continue

#         out.append(item)
#     return out


class Node:
    "Represent a node"

    name = None
    key = ""
    parent = None

    def __init__(
        self,
        name: str = None,
        key: str = None,
        parent=None,
        help: str = "",
    ):
        """
        :param key:     Name of the value used in file or environment
                        variable. Set automatically by the metaclass.
        :param help:    Plain-text description of the value.
        """
        self.key = key or self.key
        self.parent = parent or None
        self.name = name or self.name or self.key or "" or self.__class__.__name__

        self._help = help

        # Enable instance logging
        _fqn = ".".join([self.__module__, self.__class__.__qualname__])
        self._logger_name = ".".join([_fqn, str(hex(id(self)))])
        self.log = logging.getLogger(self._logger_name)
        self.log.debug(f"Create new node: {self}")


class NodeContainer(Node):
    "Represent a container"

    def __init__(self, *args, **kwargs):
        super(NodeContainer, self).__init__(*args, **kwargs)

        self._children = UNSET

        # PRepare closest type
        mro = self.__class__.__mro__
        closest = [x.__name__ for x in mro if x.__name__.startswith("Store")]
        closest = closest[0] if len(closest) > 0 else "???"
        self.closest_type = closest

    @property
    def fname(self):
        """I'm the 'x' property."""
        _t = self.get_hier(mode="full")
        _t = [x.key for x in _t]
        # _t = [x.key or x.name or "__root__" for x in _t]
        # _t = [x.name or x.key or "__root__" for x in _t]
        _t = list(reversed(_t))
        return ".".join(_t) or self.name

    # Key management (based on parents and children)
    def get_key(self, mode="self"):
        "Return object key, eventually with parent"

        def get_all_parent_keys():
            out = self.get_hier(mode="full")
            out = [x.key for x in out]
            return out

        if mode in ["self"]:
            return self.key
        if mode in ["full"]:
            out = get_all_parent_keys()
            return out
        if mode in ["parents"]:
            out = get_all_parent_keys()
            out = list(reversed(out))
            out = ".".join(out)
            return out
        if mode in ["children"]:
            if isinstance(self._children, dict):
                out = list(self._children.keys())
            else:
                out = []
            return out
        else:
            raise Exception(f"Unknown mode: {mode}")

    # Hiererachy methods
    def get_hier(self, mode="parents"):
        "Return hierachy"

        def get_all_parents():
            curr_parent = self
            out = []
            while curr_parent is not None:
                out.append(curr_parent)
                curr_parent = curr_parent.parent
            return out

        # Return list
        if mode in ["parents"]:
            out = get_all_parents()
            del out[0]
            return out
        if mode in ["full"]:
            out = get_all_parents()
            return out

        # Return item
        if mode in ["self"]:
            return self
        if mode in ["first"]:
            return self.parent or None
        if mode in ["root"]:
            out = get_all_parents()
            if len(out) > 0:
                out = out[-1]
            else:
                out = self
            return out
        else:
            raise Exception(f"Unknown mode: {mode}")

    # Children methods
    def get_children(self, *args):
        "Return one or all children inst as dict"

        children = self._children  # or dict()
        if len(args) == 0:
            return children
        else:
            return children.get(args[0], None)

    def add_child(self, child, key=None):
        "Add a child"

        if not self._children:
            self._children = dict()


        assert isinstance(self._children, dict), f"Uninitiated _children !"
        assert isinstance(
            child, NodeContainer
        ), f"Expected NodeContainer, got: {type(child)}"

        cparent = getattr(child, "parent", None)
        if cparent is not None:
            msg = f"Node already have a parent ! {child} attached to {cparent}"
            self.log.error(msg)
            raise Exception(msg)

        key = key if key is not None else child.key
        assert key, f"Can't use this key for child: {key}"

        if not key in self._children:
            self.log.debug(f"Add child: {key}=>{child}")
            self._children[key] = child
        else:
            if self._children[key] != child:
                self.log.debug(f"Update child: {key}=>{child}")
                self._children[key] = child
            else:
                self.log.debug(f"Skip existing child: {key}=>{child}")

        # Attach child
        child.parent = self

