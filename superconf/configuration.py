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
from typing import Any, Dict, List, Optional, Union

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
        self.key = key
        self._attr = attr
        self.default = default
        self.help = help
        self.cast = cast if cast is not None else self.cast
        self.instance_class = instance_class or self.instance_class
        # Validate input
        assert self.instance_class is not None, "Instance class is required"
        # assert issubclass(self.instance_class, Leaf), f"Expected a Leaf for {self.__node_fname__}, got: {type(self.instance_class)}={self.instance_class}"
        assert (
            Leaf in self.instance_class.__mro__
        ), f"Got: {self.instance_class.__mro__}"

    def get_attr(self):
        "Attribute"
        if self._attr is None:
            return self.key
        return self._attr

    # @property
    # def attr(self):
    #     "Attribute"
    #     if self._attr is None:
    #         return self.key
    #     return self._attr

    # @attr.setter
    # def attr(self, value):
    #     self._attr = value


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
# Helpers
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


def node_cast_value(self, value):
    "Cast value"

    def _cast(value):
        # If there is no cast callable, then return directly the value
        if self.__node_cast__ is None:
            return value

        # Otherwise, try to cast the value
        try:
            # msg = f"Cast value {self.__node_fname__} with {self.__node_cast__}: {value}"
            # logger.debug(msg)
            value = self.__node_cast__(value)
        except Exception as err:
            raise exceptions.InvalidCastConfiguration(
                f"Invalid cast {self.__node_cast__} for {self.__node_fname__} for value: {value}, got error: {type(err).__name__} {err}"
            )

        return value

    new_val = _cast(value)
    if new_val != value:
        msg = f"Cast value {self.__node_fname__} with {self.__node_cast__}: {value} -> {new_val}"
        logger.debug(msg)

    return new_val


class LeafConfigBase2:
    "Represent a configuration leaf"

    cast = None
    instance_class = None

    def __init__(
        self,
        default=NOT_SET,
        help="",
        cast=None,
        # attr=None,
        instance_class=None,
        attr=None,
        # instance_class=None, Nope, only for public fields !!!
        key=None,
    ):

        self.key = key
        self.default = default
        self.help = help
        self.cast = cast
        self.instance_class = instance_class
        self.attr = attr

    def __json_dump__(self):
        return self.__dict__

    def update(self, cfg):
        "Update the configuration"
        assert isinstance(cfg, dict)
        for key, val in cfg.items():

            if not hasattr(self, key):
                msg = f"Invalid field key '{key}' for {self.__class__.__name__}"
                logger.error(msg)
                print(f"ERROR TOFIX: {msg}")
                continue
                raise exceptions.InvalidField(msg)

            setattr(self, key, val)

    def __repr__(self):

        return f"LeafCfg: {self.__dict__}"

    def copy(self):
        "Copy the configuration"
        return self.__class__(**self.__dict__)


class LeafConfigCont2(LeafConfigBase2):
    "Represent a configuration leaf"

    def __init__(
        self,
        children_class=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.children_class = children_class


class LeafConfigObj2(LeafConfigCont2):
    "Represent a configuration leaf"

    def __init__(
        self,
        extra_fields=False,
        children_classes=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.extra_fields = extra_fields
        self.children_classes = children_classes


# ====================================
# Configuration Child
# ====================================


class Leaf(Node):
    "Leaf instance, representing a value"

    tmp__node_config = LeafConfigBase2(
        cast=as_is,
        default=NOT_SET,
        help=None,
    )

    __node_value__ = NOT_SET
    __node_default__ = NOT_SET
    __node_cast__ = None
    __node_field__ = None

    # Public settings
    meta__default = NOT_SET
    meta__cast = None

    def __init__(
        self,
        value: Any = NOT_SET,
        # value=UNSET_ARG,
        default=UNSET_ARG,
        key: Optional[Union[str, int]] = None,
        parent: Optional["Node"] = None,
        field=None,
    ):
        super().__init__(key=key, value=value, parent=parent)
        # print(f"++++++++ Init Leaf: {self.__node_fname__}")
        logger.debug(
            "Init node %s: %s, value=%s", self.__class__, self.__node_fname__, value
        )

        # Temporary
        # COMPAT LAYER
        new_field = self.tmp__node_config.copy()
        if field:
            tmp_val = field.__dict__
            if "_attr" in tmp_val:
                tmp_val["attr"] = tmp_val["_attr"]
                del tmp_val["_attr"]

            # print(" >>> FIELD", self, self.__class__.__mro__, new_field)
            # pprint(tmp_val)
            new_field.update(tmp_val)

        # Fetch settings overrides
        override = {
            "default": default if default is not UNSET_ARG else new_field.default,
            "cast": new_field.cast,
        }
        report = []
        default = self.__node_get_self_config__(
            "default",
            override=override,
            report=report,
        )
        cast = self.__node_get_self_config__(
            "cast",
            override=override,
            report=report,
        )

        # Configure the instance
        self.__node_field__ = new_field
        self.__node_cast__ = cast
        self.set_default(default)
        if value is UNSET_ARG or isinstance(value, NOT_SET.type):
            value = self.get_value()
        self.set_value(value)

        # Run post_load hook
        self.post_load()

    def __repr__(self):
        "Represent the instance"
        return f"{self.__class__.__name__}({self.__node_key__})"

    def set_default(self, value):
        "Set default value"

        value = self.pre_load(value)
        value = node_cast_value(self, value)
        self.__node_default__ = value

        logger.debug(
            "Set default for %s: %s", self.__node_fname__, self.__node_default__
        )
        return self.__node_default__

    def set_value(self, value):
        "Set value"
        value = self.pre_load(value)
        value = node_cast_value(self, value)
        self.__node_value__ = value

        logger.debug(
            "Set value for %s: %s (VS %s)",
            self.__node_fname__,
            self.__node_value__,
            value,
        )
        return self.__node_value__

    def get_default(self):
        "Get default value"

        default_value = self.__node_default__
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

    @property
    def __node_help__(self) -> str:
        "Get leaf help message"

        if self.__node_field__.help:
            return self.__node_field__.help

        return self.__doc__ or "<NO_HELP>"


class ContainerInstance(Leaf):
    "Container instance, either a dict or a list"

    __node_fields__ = {}
    __node_children__ = None

    meta__children_class = Leaf  # Generic children class

    def __init__(self, children_class=UNSET_ARG, **kwargs):

        # print(f"++++++++ Init ContainerInstance: {self.__node_fname__}")

        self.__node_children__ = NOT_SET

        # Fetch settings
        override = _ArgCfg()
        # override.update(
        #     {
        #         "children_class": self.__node_field__.children_class,
        #     }
        # )
        override.update(
            {
                "children_class": children_class,
            }
        )
        report = []
        self.__node_children_class__ = self.__node_get_self_config__(
            "children_class",
            override=override.cfg,
            report=report,
        )

        super().__init__(**kwargs)

    def set_value(self, *args):
        "Set value"

        if len(args) == 1:
            value = args[0]
            value = super().set_value(value)
            self.__node__set_children__(value)
            return value
        if len(args) == 2:
            key = args[0]
            value = args[1]
            self.set_key_value(key, value)
            return value

        raise SyntaxError("Invalid number of arguments")

    def __node__set_children__(self, value):
        "Set children"
        raise NotImplementedError("Subclass must implement this method")


class ConfigurationDict(ContainerInstance):
    "Dict container configuration"

    meta__cast = as_dict

    # For dict
    tmp__node_config = LeafConfigCont2(
        cast=as_dict,
        default=NOT_SET_DICT,
        help=None,
        children_class=None,
    )

    def __node__set_children__(self, value):
        "Set children from dict"

        # Skip if no children requested
        children_class = self.__node_children_class__
        if not inspect.isclass(children_class):
            logger.info("No children class defined for %s, skipping", self)
            return

        logger.info(
            "Set children for ConfigurationDict %s: %s",
            self.__node_fname__,
            truncate(value),
        )

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(value)}={value}"

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

        self.__node_children__ = children

    def get_children(self):
        "Get children"
        if isinstance(self.__node_children__, dict):
            return self.__node_children__
        return {}

    def get_child(self, key, noexceptions=False):
        "Get child"
        ret = None
        if self.__node_children__ is not NOT_SET:
            ret = self.__node_children__.get(key, None)

        if ret is not None:
            return ret

        if noexceptions is True:
            return None
        raise exceptions.UndeclaredField(
            f"Child {key} not found in {self.__node_fname__}"
        )

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"

        if key is not None:
            return self.get_key_value(key, default=default, nodefaults=nodefaults)

        if self.__node_children__ is not NOT_SET:
            ret = {}
            for key, child in self.__node_children__.items():
                ret[key] = child.get_value(nodefaults=nodefaults)

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def get_key_value(self, key, default=UNSET_ARG, nodefaults=False):
        "Get value"

        if self.__node_children__ is not NOT_SET:
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

        if self.__node_children__:
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
        if self.__node_children__ and key in self.__node_children__:
            self.__node_children__[key].set_value(value)
        else:
            super().__setattr__(key, value)

    def get(self, key, default=UNSET_ARG, mode="auto"):
        "Get a children node or an object"

        match = self.get_child(key, noexceptions=True)
        if match is not None:
            if not mode or mode == "auto":
                mode = "value"
                if hasattr(match, "__node_children__"):
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

            base_child = self.__node_children__.get(key, UNSET_ARG)
            other_child = other.__node_children__.get(key, UNSET_ARG)

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
            if hasattr(base, "__node_fields__"):
                values.update(base.__node_fields__)

        for attr, value in attrs.items():
            if isinstance(value, BaseFieldLeaf):
                values.update({attr: value})
            elif inspect.isclass(value):
                if issubclass(value, Leaf):
                    values.update({attr: value})

        attrs["__node_fields__"] = values
        attrs["meta__children_classes"] = values

        # Clean attributes
        for key in list(attrs["__node_fields__"].keys()):
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

    # For dict
    tmp__node_config = LeafConfigObj2(
        cast=as_dict,
        default=NOT_SET_DICT,
        help=None,
        extra_fields=False,
        children_class=None,
        children_classes=None,
    )

    def __init__(self, *args, **kwargs):
        "Initialize the instance"

        # print(f"++++++++ Init ContainerObj: {self.__node_fname__}")

        report = []
        self.__node_extra_fields__ = self.__node_get_self_config__(
            "extra_fields",
            report=report,
        )
        _children_raw_classes = (
            self.__node_get_self_config__(
                "children_classes",
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
                assert False, "BUG NOT SUPPORTED ANYMORE"
                if issubclass(field, Leaf):
                    field = BaseFieldContainer(field, key=attr)
                    assert isinstance(field, BaseFieldLeaf)
                else:
                    raise exceptions.InvalidField(
                        f"Expected a Leaf for {self.__node_fname__}.{attr}, got: {type(field)}={field}"
                    )

            if isinstance(field, BaseFieldLeaf):
                field.key = field.key if field.key else attr
                field.attr = attr
                _children_classes.append(field)

        self.__node_children_classes__ = _children_classes

        super().__init__(*args, **kwargs)

    def _get_child_field(self, key=None, attr=None):
        "Get child field"

        _children_classes = self.__node_children_classes__ or []
        _children_class = self.__node_children_class__ or None
        extra_fields = self.__node_extra_fields__

        child_key = key or attr
        assert child_key is not None, "Key or attr is required"

        # Search best match field
        matches = []
        for field in _children_classes:
            if key and field.key == key:
                matches.append(field)
            elif attr and field.attr == attr:
                matches.append(field)

        field = None
        if len(matches) == 1:
            field = matches[0]
        if len(matches) > 1:
            raise exceptions.InvalidCastConfiguration(
                f"Multiple child fields found for {self.__node_fname__}: {matches}"
            )

        # Handle extra fields
        if field is None:
            if extra_fields == "warn":
                logger.warning(
                    "Key '%s' is not declared in %s, use extra_fields=True to allow unknown keys",
                    child_key,
                    self.__node_fname__,
                )
            if extra_fields is False:
                raise exceptions.UndeclaredField(
                    f"Key '{child_key}' is not declared in {self.__node_fname__}, use extra_fields=True to allow unknown keys"
                )
            field = BaseFieldLeaf(key=key, attr=attr, instance_class=_children_class)

        # Check field result
        if not isinstance(field, BaseFieldLeaf):
            raise exceptions.InvalidField(
                f"Expected a BaseFieldLeaf for {self.__node_fname__}.{child_key}, got: {type(field)}={field}"
            )

        return field

    def __node__set_children__(self, value):
        "Set children"

        logger.info(
            "Set children for ConfigurationObj %s: %s",
            self.__node_fname__,
            truncate(value),
        )

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(value)}={value}"

        # Build children keys
        # -----------------------
        available_fields = []
        # Feed known fields from children_classes
        available_fields.extend(
            [field.key for field in self.__node_children_classes__ or []]
        )
        # Feed known fields from default node value
        node_default_dict = self.get_default() or {}
        available_fields.extend(list(node_default_dict.keys()))
        # Feed known fields from value
        available_fields.extend(list(value.keys()))
        # Remove duplicates
        available_fields = unique(available_fields)

        # Instanciate children
        # -----------------------
        children = OrderedDict()
        for child_key in available_fields:

            # Fetch field config overrides
            child_field = self._get_child_field(key=child_key)
            child_cls = child_field.instance_class

            # Skip if field is not valid class
            if not child_cls:  # if None of False, then skip
                continue
            assert inspect.isclass(
                child_cls
            ), f"Expected a class for {self.__node_fname__}.{child_key}, got: {type(child_cls)}={child_cls}"

            # Build field default and value
            child_default = node_default_dict.get(child_key, child_field.default)
            child_value = value.get(child_key, NOT_SET)

            # Generate child instance
            child = child_cls(
                parent=self,
                key=child_key,
                default=child_default,
                value=child_value,
                field=child_field,
            )
            children[child_key] = child

        self.__node_children__ = children


class ConfigurationList(ConfigurationDict):
    "List container configuration"

    meta__cast = as_list

    # For list
    tmp__node_config = LeafConfigCont2(
        cast=as_list,
        default=NOT_SET_LIST,
        help=None,
        children_class=None,
    )

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"
        if key is not None:
            return self.get_key_value(key, nodefaults=nodefaults, default=default)

        if self.__node_children__ is not NOT_SET:
            ret = []
            for key, child in self.__node_children__.items():
                ret.append(child.get_value(nodefaults=nodefaults))

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def __node__set_children__(self, value):
        "Set children from list"

        # Skip if no children requested
        children_class = self.__node_children_class__
        if not inspect.isclass(children_class):
            logger.info("No children class defined for %s, skipping", self)
            return

        logger.info(
            "Set children for Containerlist %s: %s",
            self.__node_fname__,
            truncate(value),
        )

        assert isinstance(
            value, list
        ), f"Expected a list for {self.__node_fname__}, got: {type(value)}={value}"

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

        self.__node_children__ = children
