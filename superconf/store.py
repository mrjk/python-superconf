"""
Represent Stores
"""

import inspect

import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .common import NOT_SET, UNSET, UnSet
from .common import list_to_dict, dict_to_list, dict_to_json
from .loaders import Environment
from .node import NodeContainer
from .mixin import StoreValueEnvVars, StoreExtra
from . import exceptions

log = logging.getLogger(__name__)


class DefaultValue:

    def __str__(self):
        return "<DEFAULT_VALUE>"


class UnsetValue:

    def __str__(self):
        return "<UNSET_VALUE>"


DEFAULT_VALUE = DefaultValue()
UNSET_VALUE = UnsetValue()


def store_to_json(obj):
    "Return a node object to serializable thing"

    def t_funct(item):
        # return str(item)

        if item is UNSET:
            return None
        if hasattr(item, "get_value"):
            return item.get_value()
        raise Exception(f"Unparseable item: {item}")

    return dict_to_json(obj, fn=t_funct)


################## Config Models


class StoreValue(NodeContainer, StoreValueEnvVars, StoreExtra):
    "Represent a node value, dead leaf"

    _default = UNSET
    _value = UNSET

    # Disable children when set to None
    _children_class = None
    _native_type = str

    class Meta:
        pass

    def __init__(
        self,
        *args,
        index=None,
        key: str = None,
        help: str = "",
        value=UNSET,
        default=UNSET,
        loaders=None,
        **kwargs,
    ):
        """
        :param key:     Name of the value used in file or environment
                        variable. Set automatically by the metaclass.
        :param help:    Plain-text description of the value.
        :param logger_mode:  Determine logger_mode.
        :param logger_prefix:  Determine logger_prefix.
        """

        self._item_class = UNSET
        assert isinstance(index, (str, int, type(None)))

        super(StoreValue, self).__init__(*args, **kwargs)

        # Set store elements
        self.key = key or self.key
        self._help = help

        # Prepare closest type
        mro = self.__class__.__mro__
        closest = [x.__name__ for x in mro if x.__name__.startswith("Store")]
        closest = closest[0] if len(closest) > 0 else "???"
        self.closest_type = closest

        # PRepare other stuffs
        self._index = index
        self._value = value if value is not UNSET else self._value
        self._default = default if default != UNSET else self._default

    def to_json(self):
        "Return json value of ..."
        return store_to_json(self)

    # Node overrides (TEMP)
    # -----------------
    def add_child(self, child, key=None, **kwargs):
        "Add a child"

        super(StoreValue, self).add_child(child, name=key, name_attr="key", **kwargs)

    # Key management (based on parents and children)
    # -------------------------------
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

    # Value methods
    # -----------------
    def get_index(self):
        "Return object parent index"
        return self._index

    def get_value(self, kind=None):
        "Get current value of config, exclude NOT_SET values"

        # Check from direct override
        value = getattr(self, "_value", UNSET)
        if value != DEFAULT_VALUE and value != UNSET:
            if kind is not None:
                if not isinstance(value, kind):
                    return None
            return value

        # If value is not present, return default instead
        return self.get_default()

    def get_default(self):
        "Get default values"

        # Check default override value
        out = getattr(self, "_default", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            # print ("RUN get_default: StoreValue - Attribute", self, out)
            return out

        # Check default from Metadata
        out = getattr(self.Meta, "default", UNSET)
        if out != DEFAULT_VALUE and out != UNSET:
            # print ("RUN get_default: StoreValue - Meta", self, out)
            return out

        # print ("RUN get_default: StoreValue - FAllBack", self, UNSET)
        return UNSET

    # Children methods
    # -----------------
    def get_children_stores(self, mode="all", lvl=-1):
        """Return a flat list of all children stores
        Allow to filter per type
        """

        out1 = [self]

        if mode == "keys":
            if isinstance(self, StoreDict):
                # Remove container keys
                out1 = []
        elif mode == "containers":
            if not isinstance(self, StoreDict):
                # Remove all keysValues
                out1 = []
        elif mode != "all":
            raise Exception(f"UNknonw mode: {mode}")

        children = self.get_children()
        for key, child in children.items():
            ret = child.get_children_stores(mode=mode, lvl=lvl)
            out1.extend(ret)

        out1 = list(set(out1))

        return out1

    def get_children_class(self, default=None):
        "Return default class to use for new children, must return a StoreNode class or UNSET"

        # Check from direct override
        out = self._item_class
        if out != UNSET:
            assert isinstance(out, (NodeContainer, type(None)))
            # print("RUN get_children_class: get_children_class - _item_class", self, out)
            return out

        # Check from Metadata
        out = getattr(self.Meta, "item_class", UNSET)
        if out != UNSET:
            assert issubclass(out, (NodeContainer, UnSet, type(None)))
            # print("RUN get_children_class: get_children_class - Meta", self, out)
            return out

        # Check from children class
        out = self._children_class
        if out != UNSET:

            if inspect.isclass(out):
                assert issubclass(out, StoreValue)
            else:
                assert isinstance(out, type(None)), f"Got: {out}"
            return out

        # Return Native type
        # # out = getattr(self, "_native_type", UNSET)
        # out = self._native_type
        # if out != UNSET:
        #     # print("RUN get_children_class: get_children_class - Native", self, out)
        #     return out

        # print("RUN get_children_class: get_children_class - NotFound", self, default)
        return default

    # Dunder methods
    # -----------------

    def __str__(self):
        addr = hex(id(self))
        value = None
        # try:
        #     value = self.get_value()
        # except AttributeError:
        #     pass

        if isinstance(value, dict):
            value = "keys=" + str(tuple(value.keys()))
            # value = f"[{value}]"
        name = self.fname
        # out = f"{name}({addr})={value}"
        out = f"{name}.???[{value}]"
        if hasattr(self, "closest_type"):
            middle = f"{self.__class__.__name__}/{self.closest_type}"
            if str(self.__class__.__name__) == str(self.closest_type):
                middle = str(self.__class__.__name__)
            out = f"{name}|{middle}[{value}]"
        return out

    # Goodies
    # ----


## ---


class StoreContainer(StoreValue):
    "Represent a unknown keys config"

    _native_type = dict
    _children_class = StoreValue

    # Container methods
    # -----------------

    def __init__(self, *args, **kwargs):

        super(StoreContainer, self).__init__(*args, **kwargs)
        native_type = self._native_type

        # Sanity checks
        value = self.get_value()
        assert isinstance(value, (native_type, UnSet)), f"Got: {value}"

        default = self.get_default()
        assert isinstance(default, (native_type, UnSet))

        self._init_children()

        assert isinstance(self._children, (dict, UnSet))

    # Value methods
    # -----------------
    def get_value(self):
        "Always return a dict"
        native_type = self._native_type

        if self._children == UNSET:
            out = super(StoreContainer, self).get_value()
            out = native_type() if not out else out
            # out = native_type() if out is None else out

            if not isinstance(out, (native_type, UNSET.__class__)):
                msg = f"Expected {native_type} for value in {self}, got {type(out)}: {out}"
                raise exceptions.InvalidValueType(msg)
            return out

        out = native_type()
        if len(self._children) > 0:
            for key, child in self._iter_children():
                if native_type == dict:
                    out[key] = child.get_value()
                elif native_type == list:
                    out.append(child.get_value())
                else:
                    raise exceptions.InvalidContainerType("Unsupported type")

        assert isinstance(
            out, (native_type, UNSET.__class__)
        ), f"Expected {native_type}, Got: {type(out)}"

        return out

    def get_default(self):
        "Top level function to get current value of config, exclude NOT_SET values"
        native_type = self._native_type

        out = super(StoreContainer, self).get_default()
        if out != UNSET:
            # print ("RUN get_default: StoreContainer - up_in_hier", self, out)
            if not isinstance(out, (native_type)):
                msg = f"Expected {native_type} for default in {self}, got {type(out)}: {out}"
                raise exceptions.InvalidContainerDefault(msg)
            return out

        # print ("RUN get_default: StoreContainer - Hard coded", self, dict())
        return native_type()

    def _iter_children(self):
        "Iterator over children"
        # Iterate over children payloads
        yield from self._children.items()

    # Dunder methods
    # -----------------
    def __getitem__(self, value):
        children = getattr(self, "_children", {})
        child = children.get(value)
        return child

    def __iter__(self):
        children = getattr(self, "_children", {})
        yield from children.items()

    def __contains__(self, value):
        children = getattr(self, "_children", {})
        return value in children

    def __len__(self):
        children = getattr(self, "_children", {})
        return len(children)


class StoreDict(StoreContainer):
    "Represent a unknown keys config"

    # Container methods
    # -----------------

    def _iter_value(self):
        yield from self.get_value().items()

    def _init_children(self):

        # Fetch current value - dict
        local_default = self.get_default()
        local_value = self.get_value()
        local_cls = self.get_children_class(default=UNSET)

        for key, val in self._iter_value():
            assert isinstance(key, str), "Invalid key"

            source = None
            local_default_subkey = local_default.get(key, UNSET)
            local_value_subkey = local_value.get(key, UNSET)

            # As Value
            if isinstance(val, Value):
                source = f"Value: {val}"
                _child_value = local_value_subkey
                # print ("NEW CHILD FROM Value", key, "from data", type(val), "default=", _child_default)
                inst = val

            # As Store
            elif isinstance(val, StoreValue):
                source = f"Store: {val}"
                _child_value = local_value_subkey
                # print ("NEW CHILD FROM StoreValue", key, "from", type(val))
                inst = val

            # As random Dict
            else:
                source = f"dict: {val}"
                _child_value = val
                # print ("NEW CHILD FROM Dict", key, "from", type(val))
                inst = local_cls(value=val, default=local_default_subkey)

            _child_default = inst.get_default()
            # TOFIX/TODO
            # _child_value2 = inst.get_value() # Broken ? Should work now
            # print ("CHILD VALUE", key, _child_value, _child_value2)

            # Check if have a child class or skip key
            _child_cls = inst.get_children_class(default=StoreValue)
            if _child_cls is None:
                continue
            assert issubclass(
                _child_cls, StoreValue
            ), f"Got: ({self}) {_child_cls} {type(_child_cls)}"

            # Determine child config
            # ------------------------------
            if _child_default == UNSET:
                # FAllback on parent value if not provided at Value
                _child_default = local_default_subkey

            if (
                _child_value == UNSET or _child_value == DEFAULT_VALUE
            ):  # or not _child_value:
                # FAllback on default if no values
                _child_value = _child_default

            if not key in self._children:
                self.log.debug(
                    f"Instanciate dict item {_child_cls}({key})=(default={_child_default}, value={_child_value})"
                )
                # Instanciate child
                assert issubclass(
                    _child_cls, StoreValue
                ), f"Must be an class of StoreValue"
                inst = _child_cls(
                    key=key, index=key, value=_child_value, default=_child_default
                )
                self.add_child(inst)


class StoreConf(StoreDict):
    "Represent a known keys config"

    def _iter_value(self):
        # Iterate over children payloads instead of values
        yield from getattr(self, "_declared_values", {}).items()

    def get_default(self):
        "Top level function to get current value of config, exclude NOT_SET values"

        out = super(StoreDict, self).get_default()
        if out != UNSET:
            # print ("RUN get_default: StoreConf - up_in_hier", self, out)
            assert isinstance(out, dict)
            return out

        # Return preset if unset
        out = getattr(self, "_declared_values", {})
        out = {k: v.get_default() for k, v in out.items()}
        # print("RUN get_default: StoreConf - generated", self, out)
        return out


class StoreList(StoreContainer):
    "Represent a unknown list config"

    _native_type = list

    # Container methods
    # -----------------

    def _iter_value(self, _start=0):

        for item in self.get_value():
            yield str(_start), item
            _start += 1

    def _init_children(self):

        # Fetch current value - dict
        local_value = self.get_value()
        local_default = self.get_default()
        local_cls = self.get_children_class(default=StoreValue)

        if local_cls is None:
            return

        _child_cls = local_cls

        for key, val in self._iter_value():
            assert isinstance(key, str), "Invalid key"

            idx = int(key)
            local_default_subkey = UNSET
            if len(local_default) > idx:
                local_default_subkey = local_default[idx]

            if not key in self._children:
                # self.log.debug(f"Instanciate list item: {key}, {_child_cls}")
                value = val
                if value == DEFAULT_VALUE or value == UNSET:  # or not value:
                    # Fetch value from parent value
                    value = local_default_subkey
                if value == DEFAULT_VALUE or value == UNSET:  # or not value:
                    # Fetch value from Item Class
                    value = local_cls().get_default()

                assert issubclass(
                    _child_cls, StoreValue
                ), f"Must be an class of StoreValue"
                inst = _child_cls(key=key, index=idx, value=value)
                self.add_child(inst)


################################### Values


class Value(StoreValue):
    "Value Node, without children"

    _children_class = StoreValue

    def __init__(self, *args, item_class=UNSET, **kwargs):

        self._children_class = (
            self._children_class if item_class == UNSET else item_class
        )
        assert issubclass(
            self._children_class, StoreValue
        ), f"Got: {self._children_class}"
        super(Value, self).__init__(*args, **kwargs)


class ValueConf(Value):
    "Value to another direct conf"

    _children_class = StoreConf


class ValueDict(Value):
    "Value to another Dict of conf"

    def __init__(self, *args, item_class=UNSET, **kwargs):

        sub_children_class = self._children_class if item_class == UNSET else item_class
        parent_class = StoreDict
        parent_class._item_class = sub_children_class
        super(ValueDict, self).__init__(*args, item_class=parent_class, **kwargs)


class ValueList(Value):
    "Value to another List of conf"

    def __init__(self, *args, item_class=UNSET, **kwargs):

        sub_children_class = self._children_class if item_class == UNSET else item_class
        parent_class = StoreList
        parent_class._item_class = sub_children_class
        super(ValueList, self).__init__(*args, item_class=parent_class, **kwargs)
