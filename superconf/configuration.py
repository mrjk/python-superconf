import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .loaders import NOT_SET, UNSET, UnSet, Environment


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
        self.key = key or ""
        self.parent = parent or None

        name = name or self.key or "" or self.__class__.__name__
        # if not name:
        #     name = f"{self.__class__.__name__}[]"
        # else:
        #     name = f"{self.__class__.__name__}[{name}]"
        self.name = name
        # self.fname = None

        # self.name = name
        # parts = [name or self.__class__.__name__, self.key]
        # # parts.extend(self.)
        # parts = [x for x in parts if x is not None]
        # self.name = ".".join((parts))

        self._fqn = ".".join([self.__module__, self.__class__.__qualname__])
        self._inst_repr = ".".join([self._fqn, str(hex(id(self)))])

        self._help = help

        # Enable instance logging
        self.log = logging.getLogger(self._inst_repr)
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
        _t = [x.key or x.name or "__root__" for x in _t]
        _t = list(reversed(_t))
        return ".".join(_t) or self.name

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

    # def has_child(self, child=None):
    # if key is None:
    #     matches = [inst for key, inst in self._children.items() if inst == child]
    #     if len(matches) > 0:
    #         key = matches[0]
    # if key is None:
    #     key = child.key

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


###################################


################## Config Models


class StoreValue(NodeContainer):
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

    # Value methods
    def get_value(self, type=None):
        "Top level function to get current value of config, exclude NOT_SET values"
        value = getattr(self, "_value", UNSET)
        if value != UNSET:
            if type is not None:
                if not isinstance(value, type):
                    return None
            return value

        # If value is not present, return default
        return self.get_default()

    def get_default(self):
        "Top level function to get default values"

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

    def get_item_cls(self, default=None):
        "Top level function to get items class"

        out = self._children_class
        if out != UNSET:
            print("RUN get_item_cls: StoreValue - _children_class", self, out)
            return out

        # Check Metadata
        out = getattr(self.Meta, "item_class", UNSET)
        if out != UNSET:
            return out

        return default

    # Helper method
    def explain(self, lvl=-1):

        print(f"===> Tree of {self.closest_type}: {self} <===")
        print(f"  inst      => {hex(id((self)))}")
        print(f"  mro       => {self.__class__.__mro__}")
        print(f"  key       => {self.key}")
        print(f"  name      => {self.name}")
        print(f"  fname     => {self.fname}")
        print(f"  default   => {str(self.get_default())}")
        print(f"  value     => {str(self.get_value())}")
        print(f"  parents   => {[str(x) for x in self.get_hier(mode='full')]}")
        print(f"  children cls  => {str(self.get_item_cls())}")
        print(f"  children  => {len(self._children)}")

        children = self._children
        for key, child in children.items():
            print(f"    {key:<20} => {str(child)}")

        print()

    def __DEFAULT_repr(self):
        addr = hex(id(self))
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        out = f"<{name} object at {addr}>"
        return out

    def __SHORT_repr(self):
        addr = hex(id(self))
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        out = f"<{name}({addr})>"
        return out

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

    # __repr__ = __str__


## ---


class StoreDict(StoreValue):
    "Represent a unknown keys config"

    # _default = dict()

    _children_class = StoreValue

    def _children_iterable(self):
        yield from self.get_children().items()

    def _children_def_iterable(self):
        # Iterate over children payloads
        yield from self.get_value().items()

    def __init__(self, *args, **kwargs):
        super(StoreDict, self).__init__(*args, **kwargs)

        # Sanity checks
        value = self.get_value()
        assert isinstance(value, (dict, UnSet)), f"Got: {value}"
        default = self.get_default()
        assert isinstance(default, (dict, UnSet))

        self._init_children()

    def _init_children(self):

        # Fetch current value - dict
        # local_value = self.get_value()
        local_value = self._value
        local_default = self.get_default()

        # Create children instances FROM HARDCODED VALUES
        for key, val in self._children_def_iterable():
            source = None

            override_default = self.get_default().get(key)

            if isinstance(val, Value):
                source = f"Value: {val}"
                _value_cls = val.get_item_cls(default=StoreValue)
                _value_default = val.get_default()
                _value_value = local_value.get(key, UNSET)
                # print ("NEW CHILD FROM Value", key, "from data", type(val), "default=", _value_default)

            elif isinstance(val, StoreValue):
                source = f"Store: {val}"
                _value_cls = self.get_item_cls(default=type(val))
                _value_default = val.get_default()
                _value_value = local_value.get(key, UNSET)
                # print ("NEW CHILD FROM StoreValue", key, "from", type(val))

            else:
                source = f"dict: {val}"
                _value_cls = self.get_item_cls(default=StoreValue)
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

    # Dunders
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

    # def __init__(self, *args, **kwargs):
    #     super(StoreConf, self).__init__(*args, **kwargs)

    def _children_def_iterable(self):
        # Iterate over children payloads
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
        print("RUN get_default: StoreConf - generated", self, out)
        return out


def list_to_dict(array):
    return {str(k): v for k, v in enumerate(array)}


def dict_to_list(map):
    return list(map.values())


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


################################### Dev helpers


class DeclarativeValuesMetaclass(type):
    """
    Collect Value objects declared on the base classes
    """

    def __new__(self, class_name, bases, attrs):
        # Collect values from current class and all bases.
        values = OrderedDict()
        keys = []

        log = logging.getLogger(f"{class_name}")
        log.debug(f"{class_name}: Metaclass prepare")
        # Walk through the MRO and add values from base class.
        for base in reversed(bases):
            if hasattr(base, "_declared_values"):
                log.debug(f"{class_name}: Import values from parent class {base}")
                keys.extend(list(base._declared_values.keys()))
                values.update(base._declared_values)

        # Collet class values
        for key, value in attrs.items():
            if isinstance(value, Value):
                if value.key and key != value.key:
                    msg = "Don't explicitly set keys when declaring values"
                    log.warn(msg)
                    # raise AttributeError( msg )
                # key = value.key

                log.debug(f"{class_name}: Add value '{key}': {value}")
                value.key = key
                values.update({key: value})
                keys.append(key)

        keys = set(keys)
        for key in keys:
            attrs[key] = values[key]
        #     del values[key]
        attrs["_declared_values"] = values

        return super(DeclarativeValuesMetaclass, self).__new__(
            self, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


class _ConfigurationMixin:

    def __init__(self, *args, **kwargs):
        super(_ConfigurationMixin, self).__init__(*args, **kwargs)


## Instance Public


class Configuration(
    _ConfigurationMixin, StoreConf, metaclass=DeclarativeValuesMetaclass
):
    "Represent a known keys config"


class ConfigurationDict(
    _ConfigurationMixin, StoreDict, metaclass=DeclarativeValuesMetaclass
):
    "Represent a unknown keys config"


class ConfigurationList(
    _ConfigurationMixin, StoreList, metaclass=DeclarativeValuesMetaclass
):
    "Represent a unknown list config"
