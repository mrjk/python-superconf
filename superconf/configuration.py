"Main configuratio  class"


# pylint: disable=unused-argument, too-few-public-methods, too-many-instance-attributes, use-dict-literal, protected-access, too-many-branches

import copy
import inspect
import logging
from collections import OrderedDict

# from collections import Mapping, Sequence
from collections.abc import Mapping, Sequence

# pylint: disable=unused-import
from pprint import pprint

from superconf import exceptions
from superconf.casts import (
    as_dict,
    as_is,
    as_list,
)
from superconf.common import (
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    UNSET_ARG,
    truncate,
    unique,
)
from superconf.nodes import BaseNode, Node

# from .fields2 import Field, FieldConf, BaseFieldContainer
# from .loaders import Environment


# from types import SimpleNamespace
# from typing import Callable


logger = logging.getLogger(__name__)


# ====================================
# Base Fields
# ====================================


class BaseFieldLeaf(BaseNode):
    "Represent a configuration leaf"

    cast = None
    instance_class = None

    def __init__(
        self,
        key=None,
        default=NOT_SET,
        help="",
        cast=None,
        attr=None,
        instance_class=None,
    ):
        self.__node_key__ = key
        self._attr = attr
        self.default = default
        self.help = help
        self.cast = cast if cast is not None else self.cast
        self.instance_class = instance_class or self.instance_class
        # Validate input
        assert self.instance_class is not None, "Instance class is required"
        assert (
            Leaf in self.instance_class.__mro__
        ), f"Got: {self.instance_class.__mro__}"

    @property
    def attr(self):
        "Attribute"
        if self._attr is None:
            return self.__node_key__
        return self._attr

    @attr.setter
    def attr(self, value):
        self._attr = value


class BaseFieldContainer(BaseFieldLeaf):
    "Represent a configuration class"

    instance_class = None
    children_class = None
    children_classes = None

    def __init__(
        self,
        instance_class,
        key=None,
        children_class=None,
        children_classes=None,
        **kwargs,
    ):
        self.instance_class = instance_class or self.instance_class
        self.children_class = children_class or self.children_class
        self.children_classes = children_classes or {}
        super().__init__(key=key, **kwargs)

        assert issubclass(
            self.instance_class, Leaf
        ), f"Expected a Leaf for {self.__node_fname__}, got: {type(self.children_class)}={self.children_class}"


# ====================================
# Configuration Child
# ====================================


class _ArgCfg:
    "Arg configuration"

    def __init__(self):

        self.cfg = {}

    def update(self, cfg):
        "Update the configuration"
        cfg = cfg or {}
        cfg = {k: v for k, v in cfg.items() if v not in (UNSET_ARG, NOT_SET)}
        self.cfg.update(cfg)

    # def __getitem__(self, key):
    #     "Get an item"
    #     return self.cfg[key]


class Leaf(Node):
    "Leaf instance, representing a value"

    __node_value__ = NOT_SET
    __default__ = NOT_SET
    __cast__ = None
    __field__ = None

    # Public settings
    meta__default = NOT_SET
    meta__cast = None

    def __init__(
        self,
        value=UNSET_ARG,
        default=UNSET_ARG,
        cast=UNSET_ARG,
        meta=None,
        field=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        logger.debug("Init node %s: %s, value=%s", self.__class__, self.__node_fname__, value)

        self.configure(value=value, default=default, meta=meta, cast=cast, field=field)

    def is_container(self):
        "Check if the instance is a container"
        return hasattr(self, "__children__")

    def __repr__(self):
        "Represent the instance"
        return f"{self.__class__.__name__}({self.__node_key__})"

    def configure(
        self, value=UNSET_ARG, default=UNSET_ARG, cast=UNSET_ARG, meta=None, field=None
    ):
        "Initialize the instance"

        # Fetch settings
        override = _ArgCfg()
        override.update(meta)
        override.update(
            {
                "cast": field.cast if field else UNSET_ARG,
            }
        )
        override.update(
            {
                "default": default,
                "cast": cast,
            }
        )

        report = []
        default = self.query_inst_cfg(
            "default",
            override=override.cfg,
            report=report,
        )
        cast = self.query_inst_cfg(
            "cast",
            override=override.cfg,
            report=report,
        )

        # Configure the instance
        self.__field__ = field
        self.__cast__ = cast
        self.set_default(default)
        if value is UNSET_ARG:
            value = self.get_value()
        self.set_value(value)

        # Run post_load hook
        self.post_load()

    def set_default(self, value):
        "Set default value"

        value = self.pre_load(value)
        value = self._cast_value(value)
        self.__default__ = value

        logger.debug("Set default for %s: %s", self.__node_fname__, self.__default__)
        return self.__default__

    def set_value(self, value):
        "Set value"
        value = self.pre_load(value)
        value = self._cast_value(value)
        self.__node_value__ = value

        logger.debug(
            "Set value for %s: %s (VS %s)", self.__node_fname__, self.__node_value__, value
        )
        return self.__node_value__

    def _cast_value(self, value):
        "Cast value"

        def _cast(value):
            # If there is no cast callable, then return directly the value
            if self.__cast__ is None:
                return value

            # Otherwise, try to cast the value
            try:
                # msg = f"Cast value {self.__node_fname__} with {self.__cast__}: {value}"
                # logger.debug(msg)
                value = self.__cast__(value)
            except Exception as err:
                raise exceptions.InvalidCastConfiguration(
                    f"Invalid cast {self.__cast__} for {self.__node_fname__} for value: {value}, got error: {type(err).__name__} {err}"
                )

            return value

        new_val = _cast(value)
        if new_val != value:
            msg = f"Cast value {self.__node_fname__} with {self.__cast__}: {value} -> {new_val}"
            logger.debug(msg)

        return new_val

    def get_default(self):
        "Get default value"

        default_value = self.__default__
        if callable(default_value):
            default_value = default_value(self)

        default_value = self.post_dump(default_value)
        return default_value

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"

        if key is not None:
            raise NotImplementedError("Keyed value not implemented")

        def _get_value(default=default, nodefaults=nodefaults):
            if self.__node_value__ is not NOT_SET:
                return self.__node_value__
            if nodefaults:
                return NOT_SET

            if default == UNSET_ARG:
                default = self.get_default()
            return default

        ret = _get_value()
        ret = self.post_dump(ret)
        return ret

    def pre_load(self, value):
        "Pre-load value user hook"
        return value

    def post_load(self):
        "Post-load value user hook"
        return

    def post_dump(self, value):
        "Post-dump value user hook"
        return value

    def merge(self, other):
        "Merge and override object with other"

        if not isinstance(other, Leaf):
            raise ValueError("Cannot merge non-Leaf")

        other_val = other.get_value(nodefaults=True)
        if not isinstance(other_val, NOT_SET.type):
            msg = f"Override Leaf {self.__class__.__name__}({self.__node_fname__}) with {other.__class__.__name__}({other.__node_fname__})"
            logger.info(msg)
            return other

        msg = f"Keep Leaf {self.__class__.__name__}({self.__node_fname__}) over {other.__class__.__name__}({other.__node_fname__})"
        logger.info(msg)
        return self

    def get_help(self) -> str:
        "Get leaf help message"

        if self.__field__ is not None and self.__field__.help:
            return self.__field__.help

        return self.__doc__ or "<NO_HELP>"


class ContainerInstance(Leaf):
    "Container instance, either a dict or a list"

    __fields__ = {}
    __children__ = None

    meta__children_class = Leaf  # Generic children class

    def __init__(self, children_class=UNSET_ARG, meta=None, **kwargs):

        self.__children__ = NOT_SET

        # Fetch settings
        override = _ArgCfg()
        override.update(meta)
        override.update(
            {
                "children_class": children_class,
            }
        )

        report = []
        self._children_class = self.query_inst_cfg(
            "children_class",
            override=override.cfg,
            report=report,
        )

        super().__init__(meta=meta, **kwargs)

    def set_value(self, *args):
        "Set value"

        if len(args) == 1:
            value = args[0]
            value = super().set_value(value)
            self._set_children(value)
            return value
        if len(args) == 2:
            key = args[0]
            value = args[1]
            self.set_key_value(key, value)
            return value

        raise SyntaxError("Invalid number of arguments")

    def _set_children(self, value):
        "Set children"
        raise NotImplementedError("Subclass must implement this method")


class ConfigurationDict(ContainerInstance):
    "Dict container configuration"

    meta__cast = as_dict

    def _set_children(self, value):
        "Set children"

        logger.info(
            "Set children for ConfigurationDict %s: %s", self.__node_fname__, truncate(value)
        )

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(value)}={value}"

        # Skip if no children requested
        children_class = self._children_class
        if children_class is None or children_class is False:
            logger.info("No children class defined for %s, skipping", self)
            return

        # Instanciate children
        children = {}
        for key, val in value.items():
            logger.info(
                "Instanciate child %s: %s(%s)",
                key,
                children_class.__name__,
                truncate(val),
            )

            child = children_class(parent=self, key=key, value=val)
            children[key] = child

        self.__children__ = children

    def get_children(self):
        "Get children"
        if isinstance(self.__children__, dict):
            return self.__children__
        return {}

    def get_child(self, key, noexceptions=False):
        "Get child"
        ret = None
        if self.__children__ is not NOT_SET:
            ret = self.__children__.get(key, None)

        if ret is not None:
            return ret

        if noexceptions is True:
            return None
        raise exceptions.UndeclaredField(f"Child {key} not found in {self.__node_fname__}")

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"

        if key is not None:
            return self.get_key_value(key, default=default, nodefaults=nodefaults)

        if self.__children__ is not NOT_SET:
            ret = {}
            for key, child in self.__children__.items():
                ret[key] = child.get_value(nodefaults=nodefaults)

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def get_key_value(self, key, default=UNSET_ARG, nodefaults=False):
        "Get value"

        if self.__children__ is not NOT_SET:
            noexceptions = True if default != UNSET_ARG else False
            child = self.get_child(key, noexceptions=noexceptions)
            if child is None and default != UNSET_ARG:
                return default
            return child.get_value(default=default, nodefaults=nodefaults)

        if default == UNSET_ARG:
            default = super().get_default()

        return default.get(key, UNSET_ARG)

    def set_key_value(self, key, value):
        "Set key value"
        child = self.get_child(key)
        child.set_value(value)

    def __contains__(self, key):
        "Check if key is in children"
        return key in self.get_children()

    def __len__(self):
        "Length"
        return len(self.get_children())

    def __iter__(self):
        "Iterate over children"

        if self.__children__:
            return iter(self.get_children().values())
        return iter([])

    def __call__(self, key):
        "Call"
        return self.get(key, mode="node")

    def __getitem__(self, key):
        "Get item. always return value"

        try:
            return self.get(key, mode="value")
        except exceptions.UnknownChild:
            raise KeyError(f"{self.__class__.__name__} has no children {key}") from None

    def __getattr__(self, key):
        "Get attribute, return value on leaf, return container otherwise"

        try:
            return self.get(key, mode="auto")
        except exceptions.UnknownChild:
            raise AttributeError(
                f"{self.__class__.__name__} has no attribute {key}"
            ) from None

    def __setattr__(self, key, value):
        "Set attribute"
        if self.__children__ and key in self.__children__:
            self.__children__[key].set_value(value)
        else:
            super().__setattr__(key, value)

    def get(self, key, default=UNSET_ARG, mode="auto"):
        "Get a children node or an object"

        match = self.get_child(key, noexceptions=True)
        if match is not None:
            if not mode or mode == "auto":
                mode = "value"
                if match.is_container():
                    mode = "node"

            if mode == "value":
                ret = match.get_value()
                return ret
            if mode == "node":
                return match

            raise ValueError(f"Invalid mode {mode} for {self.__class__.__name__}.{key}")

        if default is not UNSET_ARG:
            return default

        raise exceptions.UnknownChild(
            f"{self.__class__.__name__} has no children {key}"
        )

    def items(self):
        "Items"
        return self.get_children().items()

    def values(self):
        "Values"
        return self.get_children().values()

    def keys(self):
        "Keys"
        return self.get_children().keys()

    def merge(self, other):
        "Merge and override object with other"

        msg = f"Merge Container {self.__class__.__name__}({self.__node_fname__}) with {other.__class__.__name__}({other.__node_fname__})"
        logger.info(msg)

        if not isinstance(other, Leaf):
            raise ValueError("Cannot merge non-Leaf")

        keys = list(self.get_children().keys())
        keys.extend(list(other.get_children().keys()))
        keys = unique(keys)

        new_instance = type(self)(key=self.__node_key__)

        out = {}
        for key in keys:

            base_child = self.__children__.get(key, UNSET_ARG)
            other_child = other.__children__.get(key, UNSET_ARG)

            if base_child is not UNSET_ARG and other_child is not UNSET_ARG:
                msg = f"Merge child {key} {base_child.__node_fname__} and {other_child.__node_fname__}"
                logger.info(msg)
                tmp = base_child.merge(other_child)
                out[key] = tmp

            elif base_child is UNSET_ARG and other_child is not UNSET_ARG:
                logger.info("Add child %s %s", key, other_child.__node_fname__)
                out[key] = other_child
            elif base_child is not UNSET_ARG and other_child is UNSET_ARG:
                logger.info("Keep child %s %s", key, base_child.__node_fname__)
                out[key] = base_child
            else:
                assert False, f"Unexpected case: {key} {base_child} and {other_child}"

        for key, child in out.items():
            child.__node_parent__ = new_instance

        out = {key: child.get_value() for key, child in out.items()}
        new_instance = type(self)(value=out, key=self.__node_key__)
        return new_instance


##################


class DeclarativeValuesMetaclass(type):
    """
    Collect Value objects declared on the base classes
    """

    def __new__(mcs, class_name, bases, attrs):
        # Collect values from current class and all bases.
        values = OrderedDict()

        # Walk through the MRO and add values from base class.
        for base in reversed(bases):
            if hasattr(base, "__fields__"):
                values.update(base.__fields__)

        for attr, value in attrs.items():
            if isinstance(value, BaseFieldLeaf):
                values.update({attr: value})
            elif inspect.isclass(value):
                if issubclass(value, Leaf):
                    values.update({attr: value})

        attrs["__fields__"] = values
        attrs["meta__children_classes"] = values

        # Clean attributes
        for key in list(attrs["__fields__"].keys()):
            if key in attrs:
                del attrs[key]

        # # Clean Meta class
        # if "Meta" in attrs:
        #     attrs["__meta__"] = attrs.pop("Meta")

        return super(DeclarativeValuesMetaclass, mcs).__new__(
            mcs, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


###################


class ConfigurationObj(ConfigurationDict, metaclass=DeclarativeValuesMetaclass):
    "Keyed dict container configuration"

    # If True, allow unknown children, transformed into meta__children_class
    meta__extra_fields = False
    meta__children_classes = None

    def _get_child_field(self, key=None, attr=None, extra_fields=False):
        "Get child class"

        _children_classes = self._children_classes or []
        _children_class = self._children_class or None

        child_key = key or attr
        assert child_key is not None, "Key or attr is required"

        matches = []
        for field in _children_classes:
            if key and field.__node_key__ == key:
                matches.append(field)
            elif attr and field.attr == attr:
                matches.append(field)

        ret = None
        if len(matches) == 1:
            ret = matches[0]
        if len(matches) > 1:
            raise exceptions.InvalidCastConfiguration(
                f"Multiple child fields found for {self.__node_fname__}: {matches}"
            )

        if ret is None:
            if extra_fields == "warn":
                logger.warning(
                    "Key '%s' is not declared in %s, use extra_fields=True to allow unknown keys",
                    child_key,
                    self.__node_fname__,
                )
                ret = None
            if extra_fields is False:
                raise exceptions.UndeclaredField(
                    f"Key '{child_key}' is not declared in {self.__node_fname__}, use extra_fields=True to allow unknown keys"
                )
            ret = _children_class

        # Assert
        passed = False
        if isinstance(ret, BaseFieldLeaf):
            passed = True
            return ret, ret.instance_class
        elif inspect.isclass(ret):
            if issubclass(ret, Leaf):
                passed = True
                return (
                    BaseFieldLeaf(key=key, attr=attr, instance_class=Leaf),
                    ret,
                )
        elif ret is None:
            passed = True
            return None, None

        if not passed:
            raise exceptions.InvalidField(
                f"Expected a BaseFieldLeaf or a Leaf for {self.__node_fname__}.{child_key}, got: {type(ret)}={ret}"
            )

        return ret

    def _get_child_keys(self, attr=False):
        "Get child keys"
        _children_classes = self._children_classes or []

        if attr:
            ret = [field.attr for field in _children_classes]
        else:
            ret = [field.__node_key__ for field in _children_classes]

        return ret

    def configure(self, meta=None, **kwargs):

        # Fetch settings
        override = _ArgCfg()
        override.update(meta)

        report = []
        self._extra_fields = self.query_inst_cfg(
            "extra_fields",
            override=override.cfg,
            report=report,
        )
        _children_raw_classes = (
            self.query_inst_cfg(
                "children_classes",
                override=override.cfg,
                report=report,
            )
            or {}
        )
        assert isinstance(
            _children_raw_classes, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(_children_raw_classes)}={_children_raw_classes}"

        # Reprocess children fields
        _children_classes = []
        for attr, field in _children_raw_classes.items():

            if inspect.isclass(field):
                if issubclass(field, Leaf):
                    field = BaseFieldContainer(field, key=attr)
                    assert isinstance(field, BaseFieldLeaf)
                else:
                    raise exceptions.InvalidField(
                        f"Expected a Leaf for {self.__node_fname__}.{attr}, got: {type(field)}={field}"
                    )

            if isinstance(field, BaseFieldLeaf):
                field.__node_key__ = field.__node_key__ if field.__node_key__ else attr
                field.attr = attr
                _children_classes.append(field)
        self._children_classes = _children_classes

        super().configure(meta=meta, **kwargs)

    def _set_children(self, value):
        "Set children"

        logger.info(
            "Set children for ConfigurationObj %s: %s", self.__node_fname__, truncate(value)
        )

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(value)}={value}"

        # Prepare node elements
        node_default_dict = self.get_default() or {}
        extra_fields = self._extra_fields

        # Build children keys
        children_keys_default = []
        children_keys_default.extend(list(node_default_dict.keys()))
        children_keys_default.extend(self._get_child_keys())
        children_keys_default = unique(children_keys_default)

        # Instanciate default value
        default_children = OrderedDict()
        for child_key in children_keys_default:

            # Fetch key field
            child_field, child_cls = self._get_child_field(
                key=child_key, extra_fields=extra_fields
            )

            # Note: child_field can be one of:
            #  - None, disabled
            #  - Field instance, then we use instance_class attribute
            #  - Children class of Leaf or ContainerInstance
            if child_field is None:
                # Skip when None
                continue

            assert inspect.isclass(
                child_cls
            ), f"Expected a class for {self.__node_fname__}.{child_key}, got: {type(child_cls)}={child_cls}"

            # Get default values
            child_default = UNSET_ARG
            if child_key in node_default_dict:
                child_default = node_default_dict[child_key]
            if child_default == UNSET_ARG:
                if child_field is not None:
                    child_default = child_field.default

            # Generate child instance
            child = child_cls(
                parent=self, key=child_key, default=child_default, field=child_field
            )
            default_children[child_key] = child

        # Instanciate children
        children = {}
        children = default_children
        for key, val in value.items():

            if key in children:
                children[key].set_value(val)
            else:
                if extra_fields == "warn":
                    logger.warning(
                        "Key %s is not declared in %s, use extra_fields=True to allow unknown keys",
                        key,
                        self.__node_fname__,
                    )
                    continue
                if extra_fields is False:
                    raise exceptions.UndeclaredField(
                        f"Key {key} is not declared in {self.__node_fname__}, use extra_fields=True to allow unknown keys"
                    )

                child_field, child_cls = self._get_child_field(
                    key=key, extra_fields=extra_fields
                )

                assert child_cls is not None, "WIP"
                if child_cls:
                    logger.info(
                        "Instanciate child %s: %s(%s)",
                        key,
                        child_cls.__name__,
                        truncate(val),
                    )

                    child = child_cls(
                        parent=self, key=key, value=val, field=child_field
                    )

                    children[key] = child

        for key, child in children.items():
            assert isinstance(
                child, Leaf
            ), f"Expected a Leaf for {self.__node_fname__}.{key}, got: {type(child)}={child}"

        self.__children__ = children


class ConfigurationList(ConfigurationDict):
    "List container configuration"

    meta__cast = as_list

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"
        if key is not None:
            return self.get_key_value(key, nodefaults=nodefaults, default=default)

        if self.__children__ is not NOT_SET:
            ret = []
            for key, child in self.__children__.items():
                ret.append(child.get_value(nodefaults=nodefaults))

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def _set_children(self, value):
        "Set children"

        logger.info(
            "Set children for Containerlist %s: %s", self.__node_fname__, truncate(value)
        )

        assert isinstance(
            value, list
        ), f"Expected a list for {self.__node_fname__}, got: {type(value)}={value}"

        # Skip if no children requested
        children_class = self._children_class
        if children_class is None or children_class is False:
            logger.info("No children class defined for %s, skipping", self)
            return

        # Instanciate children
        children = {}
        for index, val in enumerate(value):
            logger.info(
                "Instanciate child %s: %s(%s)",
                index,
                children_class.__name__,
                truncate(val),
            )
            child = children_class(parent=self, key=index, value=val)
            children[index] = child

        self.__children__ = children
