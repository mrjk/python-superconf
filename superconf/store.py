"""
Represent Stores
"""

import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .common import NOT_SET, UNSET, UnSet
from .common import list_to_dict, dict_to_list, dict_to_json
from .loaders import Environment
from .node import NodeContainer
from .mixin import StoreValueEnvVars, StoreExtra

log = logging.getLogger(__name__)




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

    class Meta:
        pass

    def __init__(self, *args, value=UNSET, default=UNSET, loaders=None, **kwargs):
        """
        :param value:   Current value
        :param default: Default value if none is provided.
        """

        super(StoreValue, self).__init__(*args, **kwargs)

        self._value = value if value is not UNSET else self._value
        self._default = default if default != UNSET else self._default


    def to_json(self):
        "Return json value of ..."
        return store_to_json(self)


    # Value methods
    # -----------------
    def get_value(self, type=None):
        "Get current value of config, exclude NOT_SET values"
        value = getattr(self, "_value", UNSET)
        if value != UNSET:
            if type is not None:
                if not isinstance(value, type):
                    return None
            return value

        # If value is not present, return default
        return self.get_default()

    def get_default(self):
        "Get default values"

        # Check local value
        out = self._default
        if out != UNSET:
            # print ("RUN get_default: StoreValue - Attribute", self, out)
            return out

        # Check Metadata
        out = getattr(self.Meta, "default", UNSET)
        if out != UNSET:
            # print ("RUN get_default: StoreValue - Meta", self, out)
            return out

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
        "Return default class to use for new children"

        out = self._children_class
        if out != UNSET:
            # print("RUN get_children_class: StoreValue - _children_class", self, out)
            return out

        # Check Metadata
        out = getattr(self.Meta, "item_class", UNSET)
        if out != UNSET:
            return out

        return default



    # Dunder methods
    # -----------------

    # def __DEFAULT_repr(self):
    #     addr = hex(id(self))
    #     name = f"{self.__class__.__module__}.{self.__class__.__name__}"
    #     out = f"<{name} object at {addr}>"
    #     return out

    # def __SHORT_repr(self):
    #     addr = hex(id(self))
    #     name = f"{self.__class__.__module__}.{self.__class__.__name__}"
    #     out = f"<{name}({addr})>"
    #     return out
    # def __repr__(self):
    #     addr = hex(id(self))
    #     name = f"{self.__class__.__module__}.{self.__class__.__name__}"
    #     out = f"Confissime - <{name} object at {addr}>"
    #     return out

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


class StoreDict(StoreValue):
    "Represent a unknown keys config"


    _children_class = StoreValue

    # Container methods
    # -----------------

    def __init__(self, *args, **kwargs):
        super(StoreDict, self).__init__(*args, **kwargs)

        # Sanity checks
        value = self.get_value()
        assert isinstance(value, (dict, UnSet)), f"Got: {value}"
        default = self.get_default()
        assert isinstance(default, (dict, UnSet))

        self._init_children()


    # def _children_iterable(self):
    #     yield from self.get_children().items()

    def _children_def_iterable(self):
        # Iterate over children payloads
        yield from self.get_value().items()

    def _init_children(self):

        # Fetch current value - dict
        local_value = self.get_value()
        # local_value = self._value
        local_default = self.get_default()

        # Create children instances FROM HARDCODED VALUES
        for key, val in self._children_def_iterable():
            source = None

            override_default = self.get_default().get(key)

            if isinstance(val, Value):
                source = f"Value: {val}"
                _value_cls = val.get_children_class(default=StoreValue)
                _value_default = val.get_default()
                _value_value = local_value.get(key, UNSET)
                # print ("NEW CHILD FROM Value", key, "from data", type(val), "default=", _value_default)

            elif isinstance(val, StoreValue):
                source = f"Store: {val}"
                _value_cls = self.get_children_class(default=type(val))
                _value_default = val.get_default()
                _value_value = local_value.get(key, UNSET)
                # print ("NEW CHILD FROM StoreValue", key, "from", type(val))

            else:
                source = f"dict: {val}"
                _value_cls = self.get_children_class(default=StoreValue)
                _value_value = val
                _value_default = self.get_default().get(key, UNSET)
                # print ("NEW CHILD FROM Dict", key, "from", type(val))

            if override_default != UNSET:
                child_default = override_default
            else:
                child_default = _value_default

            if _value_cls is None:
                continue

            # self.log.debug(f"New child '{key}' ({_value_cls}): {_value_value}")
            assert issubclass(
                _value_cls, StoreValue
            ), f"Got: ({self}) {type(_value_inst)}"

            if not key in self._children:
                self.log.debug(f"Instanciate key: {key}")

                # Instanciate child
                cls = _value_cls
                assert issubclass(cls, StoreValue), f"Must be an class of StoreValue"
                child_default = local_default.get(key, None) or _value_default

                child_values = _value_value
                inst = cls(key=key, value=child_values, default=child_default)

                self.add_child(inst)

    # Value methods
    # -----------------
    def get_value(self):
        "Always return a dict"

        if self._children == UNSET:
            out = super(StoreDict, self).get_value()
            return out

        out = dict()
        if len(self._children) > 0:
            for key, child in self._children.items():
                out[key] = child.get_value()

        assert isinstance(out, (dict, UNSET.__class__)), f"Got: {type(out)}"
        return out

    def get_default(self):
        "Top level function to get current value of config, exclude NOT_SET values"

        out = super(StoreDict, self).get_default()
        if out != UNSET:
            # print ("RUN get_default: StoreDict - up_in_hier", self, out)
            assert isinstance(out, dict)
            return out

        # print ("RUN get_default: StoreDict - Hard coded", self, dict())
        return {}



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


class StoreConf(StoreDict):
    "Represent a known keys config"

    def _children_def_iterable(self):
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



class StoreList(StoreDict):
    "Represent a unknown list config"

    def __init__(self, *args, value=UNSET, default=UNSET, **kwargs):

        # Sanity checks
        # value = self.get_value()
        # assert isinstance(value, list)

        # default = self.get_default()
        # assert isinstance(default, list)

        if value != UNSET:
            value = list_to_dict(value)
        default = list_to_dict(default)

        # _value = list(values)
        super(StoreList, self).__init__(*args, value=value, default=default, **kwargs)

    # def get_default(self):
    #     "Top level function to get current value of config, exclude NOT_SET values"

    #     print ("RUN get_default: StoreList", self)

    #     # BROKEN IF DISABLED
    #     out = super(StoreList, self).get_default()
    #     if out != UNSET:
    #         return out
    #     return {}




################################### Values


class Value(StoreValue):
    "Value Node, without children"

    _children_class = StoreValue

    def __init__(self, *args, item_class=None, **kwargs):

        self._children_class = (
            self._children_class if item_class is None else item_class
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

    def __init__(self, *args, item_class=None, **kwargs):

        sub_children_class = self._children_class if item_class is None else item_class
        parent_class = StoreDict
        parent_class._children_class = sub_children_class
        super(ValueDict, self).__init__(*args, item_class=parent_class, **kwargs)


class ValueList(Value):
    "Value to another List of conf"

    def __init__(self, *args, item_class=None, **kwargs):

        sub_children_class = self._children_class if item_class is None else item_class
        parent_class = StoreList
        parent_class._children_class = sub_children_class
        super(ValueList, self).__init__(*args, item_class=parent_class, **kwargs)
