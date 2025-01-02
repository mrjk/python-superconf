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


# Top class
# ======================================

class Node:
    "Represent a node"

    _name = None
    key = ""
    parent = None

    def __init__(
        self,
        name: str = None,
        parent=None,
        logger_mode=None,
        logger_prefix=None,
    ):
        """
        :param key:     Name of the value used in file or environment
                        variable. Set automatically by the metaclass.
        :param parent:  Determine parent object, creator of the instance.
        """
        self.parent = parent or None
        self._name = name or self._name

        self.set_logger(logger_mode=logger_mode, logger_prefix=logger_prefix)

    # Properties
    # -------------------------------

    @property
    def name(self):
        """Return name as string. Empty string is returned when no name."""
        if isinstance(self._name, str):
            return self._name
        return ""

    @property
    def fname(self):
        """Return the full string name of object with parent"""
        _t = self.get_hier(mode="full")
        _t = [x.key for x in _t]
        _t = list(reversed(_t))
        return ".".join(_t) or self.name

    # Hiererachy methods
    # -------------------------------

    def get_hier(self, mode="parents"):
        "Return list of parents, last element is the root element"

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

    # Logging
    # -------------------------------

    def set_logger(self, logger_mode=None, logger_prefix=None):
        """
        Define object logger

        Modes:
          - "absent": Does not create log attribute
          - "default": Use library logger shortcut
          - "instance": Use per instance logger

        Raises:
            Exception: _description_

        Returns:
            None: Return nothing
        """

        # Validate input
        NODE_SET_LOGGER_MODES = ["absent", "default", "instance", "inherit"]

        # Determine value
        if logger_mode == None or logger_mode == "inherit":
            if self.parent:
                logger_mode = getattr(self.parent, "_logger_mode", None)
        logger_mode = logger_mode or "default"

        # Set logger mode
        if logger_mode not in NODE_SET_LOGGER_MODES:
            raise Exception(
                f"Unsupported mode '{logger_mode}', please use one of: {NODE_SET_LOGGER_MODES}"
            )
        self._logger_mode = logger_mode
        self._logger_prefix = logger_prefix

        # Check base modes
        if logger_mode in ["absent"]:
            return
        elif logger_mode in ["default"]:
            self.log = log
        else:

            logger_prefix = logger_prefix or self.__module__

            # Fetch infos
            obj_id = str(hex(id(self)))
            if logger_mode in ["class"]:
                obj_name = ".".join([logger_prefix, self.__class__.__qualname__])
            elif logger_mode in ["instance"]:
                obj_name = ".".join(
                    [logger_prefix, self.__class__.__qualname__, self.name]
                )

            # Set logger
            # logger_name = ".".join([obj_name, obj_id])
            logger_name = obj_name
            self.log = logging.getLogger(logger_name)

        # Use logger
        self.log.debug(f"Create new node: {self}")




# Second Level class
# ======================================



class DefaultValue:

    def __str__(self):
        return "<DEFAULT_VALUE>"


class UnsetValue:

    def __str__(self):
        return "<UNSET_VALUE>"


DEFAULT_VALUE = DefaultValue()
UNSET_VALUE = UnsetValue()



class NodeMeta(Node):
    "Represent a container"


    class Meta:
        "Local class configurator"


    def get_inst_cfg(self, name, default=UNSET):
        "Return instance config"

        # Check in order: 
        # - inst._NAME
        # - CLASS.Meta.NAME
        # - inst._NAME_default

        # Check default override value
        out = getattr(self, f"_{name}", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            return out

        # Check from Metadata
        out = getattr(self.Meta, name, UNSET)
        if out != UNSET:
            return out

        # Check from class inheritance
        out = getattr(self, f"{name}", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            return out

        return default





class NodeContainer(NodeMeta):
    "Represent a container"

    def __init__(self, *args, **kwargs):
        """
        Define children mode
        """

        super(NodeContainer, self).__init__(*args, **kwargs)
        self._children = UNSET


    # Dunder methods
    # -----------------
    def __getitem__(self, value):
        return self.get_children(value)
        # children = getattr(self, "_children", {})
        # child = children.get(value)
        # return child

    def __iter__(self):
        yield from self.get_children().items()

        # children = getattr(self, "_children", {})
        # yield from children.items()

    def __contains__(self, value):
        return self.get_children(value)
        # children = getattr(self, "_children", {})
        # return value in children

    def __len__(self):
        return len(self.get_children())
        # children = getattr(self, "_children", {})
        # return len(children)


    # Children
    # -------------------------------

    def get_children(self, *args):
        "Return one or all children inst as dict"

        children = self._children or dict()
        if len(args) == 0:
            return children or UNSET
        else:
            return children.get(args[0], None)

    def add_child(self, child, name=None, name_attr="name"):
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

        name = name if name is not None else getattr(child, name_attr, None)
        assert name, f"Can't use this name for child: {name}"

        if not name in self._children:
            self.log.debug(f"Add child: {name}=>{child}")
            self._children[name] = child
        else:
            if self._children[name] != child:
                self.log.debug(f"Update child: {name}=>{child}")
                self._children[name] = child
            else:
                self.log.debug(f"Skip existing child: {name}=>{child}")

        # Attach child
        child.parent = self
