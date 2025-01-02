import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .common import NOT_SET, UNSET


log = logging.getLogger(__name__)


# Top class
# ======================================

class NodeBase:
    "Represent a node"

    _name = None
    parent = None

    def __init__(
        self,
        name: str = "",
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
        self._name = name or self._name or ""

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
        out = [str(x.name) for x in self.get_parents(mode="full")]
        out = list(reversed(out))
        return ".".join(out) or self.name


    # Hiererachy methods
    # -------------------------------

    def get_parents(self, mode="parents"):
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
        NODE_SET_LOGGER_MODES = ["absent", "default", "instance", "class", "inherit"]

        # Determine value
        if logger_mode == None or logger_mode == "inherit":
            parents = self.get_parents(mode="full")
            for parent in parents:
                match = getattr(parent, "_logger_mode", "inherit")
                if match != "inherit":
                    logger_mode = match
                    break
            if logger_mode == "inherit":
                logger_mode = "instance"
        
        # 
        logger_mode = logger_mode or "default"

        # Set logger mode
        if logger_mode not in NODE_SET_LOGGER_MODES and logger_mode != "inherit":
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
            else:
                assert False, f"VALUE: {logger_mode}"

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



class NodeMeta(NodeBase):
    "Add metadata feature to each instances"


    class Meta:
        "Local class configurator"


    def get_inst_cfg(self, name, default=UNSET):
        """Return instance config
        
        Lookup order:
        - Check in: self._NAME
        - Check in: self.__class__.Meta.NAME
        - Check in: self.NAME  # TODFIX: Use self.NAME_default
        """

        # Check default override value
        out = getattr(self, f"_{name}", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            return out

        # Check from Metadata
        out = getattr(self.Meta, name, UNSET)
        if out != UNSET:
            return out

        # Check from class inheritance
        # TOFIX fallback value ?
        out = getattr(self, f"{name}", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            return out

        return default



class NodeChildren(NodeBase):
    "Manage node children"


    def __init__(self, *args, **kwargs):
        """
        Define children mode
        """

        super(NodeChildren, self).__init__(*args, **kwargs)
        self._children = UNSET


    # Dunder methods
    # -----------------
    def __getitem__(self, key):
        return self.get_children(key)

    def __iter__(self):
        yield from self.get_children().items()

    def __contains__(self, key):
        return self.get_children(key)

    def __len__(self):
        return len(self.get_children())


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
            msg = f"NodeBase already have a parent ! {child} attached to {cparent}"
            self.log.error(msg)
            raise Exception(msg)

        name = name if name is not None else getattr(child, name_attr, None)
        assert name, f"Can't use this name for child: {type(name)} {name}"

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




# Exposed Classes
# ======================================



class NodeContainer(NodeMeta,NodeChildren):
    "Represent a NodeBase container"

