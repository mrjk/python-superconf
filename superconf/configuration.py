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
from superconf.common import NOT_SET, UNSET_ARG
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
        self.__key__ = key
        self._attr = attr
        self.default = default
        self.help = help
        self.cast = cast if cast is not None else self.cast
        self.instance_class = instance_class or self.instance_class
        # Validate input
        assert self.instance_class is not None, "Instance class is required"
        assert (
            LeafInstance in self.instance_class.__mro__
        ), f"Got: {self.instance_class.__mro__}"

    # @classmethod
    # def get_default(self):
    #     "Get default value"
    #     return self.default

    @property
    def attr(self):
        "Attribute"
        if self._attr is None:
            return self.key
        return self._attr

    @attr.setter
    def attr(self, value):
        self._attr = value

    # def is_container(self):
    #     "This kind of field is never a container"
    #     return False


class BaseFieldContainer(BaseFieldLeaf):
    "Represent a configuration class"

    # def __init__(self, key=None, default=NOT_SET, help="", cast=None, child_class=None):

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

        # Validate input
        # assert isinstance(self.child_class, ContainerInstance)
        # assert not isinstance(self.child_class, LeafInstance)

        # assert not LeafInstance in self.child_class.__mro__, f"Got: {self.child_class.__mro__}"
        # assert ContainerInstance in self.child_class.__mro__, f"Got: {self.child_class.__mro__}"

        # print("CHILDREN CLASS", self.children_class)
        # pprint(self.children_class.__mro__)
        assert issubclass(
            self.instance_class, LeafInstance
        ), f"Expected a LeafInstance for {self.fname}, got: {type(self.children_class)}={self.children_class}"
        # assert issubclass(self.children_class, (LeafInstance, type(None))), f"Expected a LeafInstance for {self.fname}, got: {type(self.children_class)}={self.children_class}"
        # assert not isinstance(self.children_class, LeafInstance)

    # def is_container(self):
    #     """Check if this field is a container type.

    #     Returns:
    #         bool: True if this field has a children_class attribute,
    #         indicating it can contain nested configuration values.
    #     """
    #     # children_class = getattr(self, "children_class", None)
    #     children_class = self.children_class
    #     if children_class is not None:
    #         return True
    #     return False


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


class LeafInstance(Node):
    "Leaf instance, representing a value"

    __value__ = NOT_SET
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

        self.configure(value=value, default=default, meta=meta, cast=cast, field=field)

    def is_container(self):
        "Check if the instance is a container"
        return hasattr(self, "__children__")

    def __repr__(self):
        "Represent the instance"
        return f"{self.__class__.__name__}({self.__key__})"

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

        # pprint(override.cfg)
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

    def set_default(self, value):
        "Set default value"

        self.__default__ = self._cast_value(value)
        return self.__default__

    def get_default(self):
        "Get default value"

        default_value = self.__default__
        if callable(default_value):
            default_value = default_value(self)


        # print("RETURN DEFAULT VALUE", default_value)
        return default_value

    def get_value(self, key=None, nodefaults=False, default=UNSET_ARG):
        "Get value"

        if key is not None:
            raise NotImplementedError("Keyed value not implemented")

        def _get_value(default=default, nodefaults=nodefaults):
            if self.__value__ is not NOT_SET:
                return self.__value__
            if nodefaults:
                return NOT_SET

            if default == UNSET_ARG:
                default = self.get_default()
            return default

        ret = _get_value()
        print("GET VALUE", self.__cast__, ret)
        # if cast:
        #     ret = self._cast_value(ret)

        # if self.__cast__ is not None:
        #     ret = self.__cast__(ret)
        return ret

    def set_value(self, value):
        "Set value"
        self.__value__ = self._cast_value(value)
        return self.__value__

    def _cast_value(self, value):
        "Cast value"

        if self.__cast__ is None:
            return value
        # if value in [UNSET_ARG, NOT_SET]:
        if value is UNSET_ARG:
            return value

        print("CAST VALUE", self.fname, self.__cast__, value)

        try:
            value = self.__cast__(value)
        except Exception as e:
            raise exceptions.InvalidCastConfiguration(
                f"Invalid cast for {self.fname}: {e}"
            )

        return value


class ContainerInstance(LeafInstance):
    "Container instance, either a dict or a list"

    __fields__ = {}
    __children__ = None

    meta__children_class = LeafInstance  # Generic children class

    def __init__(self, **kwargs):

        self.__children__ = NOT_SET
        super().__init__(**kwargs)


class ContainerDict(ContainerInstance):
    "Dict container configuration"

    __cast__ = as_dict

    def configure(self, children_class=UNSET_ARG, meta=None, **kwargs):

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
        super().configure(meta=meta, **kwargs)

    def _set_children(self, value):
        "Set children"

        if value is None:
            value = {}
        if value is NOT_SET:
            value = {}

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.fname}, got: {type(value)}={value}"

        # Skip if no children requested
        children_class = self._children_class
        if children_class is None or children_class is False:
            logger.info("No children class defined for %s, skipping", self)
            return

        # Instanciate children
        children = {}
        for key, val in value.items():
            child = children_class(parent=self, key=key, value=val)
            children[key] = child

        self.__children__ = children

    def get_children(self):
        "Get children"
        if isinstance(self.__children__, dict):
            return self.__children__
        return {}

    def set_value(self, value):
        "Set value"
        value = super().set_value(value)
        self._set_children(value)
        return self.get_value()

    def get_value(self, key=None, nodefaults=False, default=UNSET_ARG):
        "Get value"
        if key is not None:
            # ret = None
            # if self.__children__ is not NOT_SET:
            #     ret = self.__children__.get(key, None)
            # return ret
            return self.get_key_value(
                key, nodefaults=nodefaults, default=default
            )

        if self.__children__ is not NOT_SET:
            ret = {}
            for key, child in self.__children__.items():
                ret[key] = child.get_value(nodefaults=nodefaults)

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def get_key_value(self, key, nodefaults=False, default=UNSET_ARG):
        "Get value"
        # print("GET KEY VALUE", self, key, default, self.__children__)

        if self.__children__ is not NOT_SET:
            child = self.__children__.get(key, UNSET_ARG)
            if child is UNSET_ARG:
                if default == UNSET_ARG:
                    raise exceptions.UndeclaredField(
                        f"Key {key} not found in {self.fname}"
                    )
                return default
            return child.get_value(nodefaults=nodefaults)

        if default == UNSET_ARG:
            default = super().get_default()

        return default.get(key, UNSET_ARG)

    # def set_key_value(self, key, value):
    #     "Set value"

    #     assert isinstance(
    #         key, str
    #     ), f"Expected a str for {self.fname}, got: {type(key)}={key}"

    #     children = self.__children__ or {}

    #     if key in children:
    #         child = children[key].set_value(value)
    #         child.set_value(value)
    #     else:
    #         raise exceptions.InvalidField(f"Key {key} not found in {self.fname}")

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
        return self.get_children()[key]

    def __getitem__(self, key):
        "Get item. always return value"

        child = self.get_children()[key]

        if child.is_container():
            ret = child
        else:
            ret = child.get_value()

        return ret

    def __getattr__(self, key):
        "Get attribute, return value on leaf, return container otherwise"

        ret = UNSET_ARG
        if self.__children__ and key in self.__children__:
            child = self.get_children()[key]
            if child.is_container():
                ret = child
            else:
                ret = child.get_value()

        if ret == UNSET_ARG:
            raise AttributeError(f"{self.__class__.__name__} has no attribute {key}")

        return ret
        # return copy.deepcopy(ret)

    def get(self, key, default=UNSET_ARG):
        "Get"
        if key in self.__children__:
            return self.__children__[key]
        return default

    def items(self):
        "Items"
        return self.get_children().items()

    def values(self):
        "Values"
        return self.get_children().values()

    def keys(self):
        "Keys"
        return self.get_children().keys()


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
                # print("SCANNING", attr, value, LeafInstance)
                # pprint(value.__mro__)
                if issubclass(value, LeafInstance):
                    # assert False, f"WIP, {attr} is a class, {value}"
                    print("UPDATE VALUES", attr, value)
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

        # print("METACLASS", mcs, class_name, bases, attrs)
        return super(DeclarativeValuesMetaclass, mcs).__new__(
            mcs, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


###################


class ContainerConf(ContainerDict, metaclass=DeclarativeValuesMetaclass):
    "Keyed dict container configuration"

    meta__extra_fields = (
        False  # If True, allow unknown children, transformed into meta__children_class
    )
    meta__children_classes = None

    def _get_child_field(self, key=None, attr=None, extra_fields=False):
        "Get child class"

        _children_classes = self._children_classes or []
        _children_class = self._children_class or None

        child_key = key or attr
        assert child_key is not None, "Key or attr is required"

        matches = []
        for field in _children_classes:
            if key and field.key == key:
                matches.append(field)
            elif attr and field.attr == attr:
                matches.append(field)

        ret = None
        if len(matches) == 1:
            ret = matches[0]
        if len(matches) > 1:
            raise exceptions.InvalidCastConfiguration(
                f"Multiple child fields found for {self.fname}: {matches}"
            )

        if ret is None:
            if extra_fields == "warn":
                logger.warning(
                    "Key %s is not declared in %s, use extra_fields=True to allow unknown keys",
                    child_key,
                    self.fname,
                )
                ret = None
            if extra_fields is False:
                raise exceptions.UndeclaredField(
                    f"Key {child_key} is not declared in {self.fname}, use extra_fields=True to allow unknown keys"
                )
            ret = _children_class
        # print("DEBUG RET", type(ret), ret)

        # Assert
        passed = False
        if isinstance(ret, BaseFieldLeaf):
            passed = True
            return ret, ret.instance_class
        elif inspect.isclass(ret):
            if issubclass(ret, LeafInstance):
                passed = True
                return (
                    BaseFieldLeaf(key=key, attr=attr, instance_class=LeafInstance),
                    ret,
                )
        elif ret is None:
            passed = True
            return None, None

        if not passed:
            raise exceptions.InvalidField(
                f"Expected a BaseFieldLeaf or a LeafInstance for {self.fname}.{child_key}, got: {type(ret)}={ret}"
            )

        return ret

    def _get_child_keys(self, attr=False):
        "Get child keys"
        _children_classes = self._children_classes or []
        print("GET CHILD KEYS", self)
        pprint(_children_classes)

        if attr:
            ret = [field.attr for field in _children_classes]
        else:
            ret = [field.key for field in _children_classes]

        # print("GET CHILD KEYS", ret)
        # pprint(self._children_classes)
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
        ), f"Expected a dict for {self.fname}, got: {type(_children_raw_classes)}={_children_raw_classes}"

        # Reprocess children fields
        _children_classes = []
        for attr, field in _children_raw_classes.items():

            if inspect.isclass(field):
                if issubclass(field, LeafInstance):
                    field = BaseFieldContainer(field, key=attr)
                    assert isinstance(field, BaseFieldLeaf)
                else:
                    raise exceptions.InvalidField(
                        f"Expected a LeafInstance for {self.fname}.{attr}, got: {type(field)}={field}"
                    )

            if isinstance(field, BaseFieldLeaf):
                field.key = field.key if field.key else attr
                field.attr = attr
                _children_classes.append(field)
        self._children_classes = _children_classes

        # print("CHILD FIELDS")
        # pprint({(v.key, v.attr, v) for v in _children_classes})
        # self._child_fields = None

        # pprint(report)

        super().configure(meta=meta, **kwargs)

    def _set_children(self, value):
        "Set children"

        # WAht does ahappend to parent

        if value is None:
            value = {}
        if value is NOT_SET:
            value = {}

        assert isinstance(
            value, dict
        ), f"Expected a dict for {self.fname}, got: {type(value)}={value}"

        # Prepare node elements
        node_default_dict = self.get_default() or {}
        # node_child_classes = self._get_child_keys()
        # node_children_class = self._children_class or None
        extra_fields = self._extra_fields

        # Build children keys
        children_keys_default = []
        children_keys_default.extend(list(node_default_dict.keys()))
        children_keys_default.extend(self._get_child_keys())
        children_keys_default = list(set(children_keys_default))

        # Instanciate default value
        default_children = {}
        for child_key in children_keys_default:

            # Fetch key field
            child_field, child_cls = self._get_child_field(
                key=child_key, extra_fields=extra_fields
            )

            # Note: child_field can be one of:
            #  - None, disabled
            #  - Field instance, then we use instance_class attribute
            #  - Children class of LeafInstance or ContainerInstance
            if child_field is None:
                # Skip when None
                continue
            # if isinstance(child_field, BaseFieldLeaf):
            #     # If child field, then grab instance_class
            #     child_cls = child_field.instance_class

            # elif inspect.isclass(child_field):
            #     if not issubclass(child_field, LeafInstance):
            #         raise exceptions.InvalidField(
            #             f"Expected a LeafInstance for {self.fname}.{child_key}, got: {type(child_field)}={child_field}"
            #         )
            #     child_cls = child_field
            #     child_field = None
            # else:
            #     assert False, f"Unexpected child field type: {type(child_field)}={child_field}"

            assert inspect.isclass(
                child_cls
            ), f"Expected a class for {self.fname}.{child_key}, got: {type(child_cls)}={child_cls}"

            # Get default values
            child_default = UNSET_ARG
            if child_key in node_default_dict:
                child_default = node_default_dict[child_key]
            if child_default == UNSET_ARG:
                if child_field is not None:
                    child_default = child_field.default
                # else:
                #     child_default = child_field.

            # print("REPROCESSING", child_key, child_field, child_default)

            # Generate child instance
            child = child_cls(
                parent=self, key=child_key, default=child_default, field=child_field
            )
            default_children[child_key] = child

        # print("DEFAULT CHILDREN vvv", self)
        # pprint(default_children)
        # print("DEFAULT CHILDREN ^^^")

        # Instanciate children
        children = {}
        children = default_children
        for key, val in value.items():

            print("REPROCESSING22", key, val)

            if key in children:
                # child =
                children[key].set_value(val)
            else:
                if extra_fields == "warn":
                    logger.warning(
                        "Key %s is not declared in %s, use extra_fields=True to allow unknown keys",
                        key,
                        self.fname,
                    )
                    continue
                if extra_fields is False:
                    raise exceptions.UndeclaredField(
                        f"Key {key} is not declared in {self.fname}, use extra_fields=True to allow unknown keys"
                    )

                child_field, child_cls = self._get_child_field(
                    key=key, extra_fields=extra_fields
                )
                # if not child_field:
                #     assert False, f"TO DEPRECATED, {type(child_field)}={child_field}"
                #     child_field = node_children_class
                # print("CHILD FIELD", key, val, child_field)
                # pprint(self.__dict__)
                print(
                    "CHILD CLASS",
                    self._children_class,
                    self.fname,
                    key,
                    extra_fields,
                    child_field,
                    child_cls,
                )
                assert child_cls is not None, "WIP"
                if child_cls:
                    child = child_cls(
                        parent=self, key=key, value=val, field=child_field
                    )

                    # assert False, "WIP undeclared children"
                    children[key] = child

        for key, child in children.items():
            assert isinstance(
                child, LeafInstance
            ), f"Expected a LeafInstance for {self.fname}.{key}, got: {type(child)}={child}"

        self.__children__ = children


class ContainerList(ContainerInstance):
    "List container configuration"

    __cast__ = as_list


# Compat layer:
Configuration = ContainerConf
ConfigurationDict = ContainerDict
ConfigurationList = ContainerList
