"""Container configuration models."""

import inspect
import logging
from collections import OrderedDict

from superconf import exceptions
from superconf.casts import as_dict, as_is, as_list
from superconf.common import (
    MERGE_DICT_DEFAULT,
    MERGE_LIST_DEFAULT,
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    UNSET_ARG,
    merge_data,
    merge_maps,
    truncate,
    unique,
)
from superconf.leaf import (
    GenericField,
    Leaf,
    LeafContainerConfig,
    LeafObjConfig,
    PublicField,
)
from superconf.merge import MergeKind

logger = logging.getLogger(__name__)


class _ContainerInstance(Leaf):
    "Container instance, either a dict or a list"

    __node_fields__ = {}
    __node_children__ = None

    __node_config__ = LeafContainerConfig(
        cast=as_is,
        default=NOT_SET,
        help=None,
        children_class=Leaf,
    )

    def __node_init__(self, **kwargs):
        "Prepare Container instance"

        # Call parent init
        children_class = kwargs.pop("children_class", UNSET_ARG)
        super().__node_init__(**kwargs)

        # Configure instance
        self.__node_children__ = {}

        # Fetch node_children_class settings
        _report = []
        _children_class = self.__node_get_self_config__(
            "children_class",
            overrides=[
                children_class,
                self.__node_field__.query("children_class"),
            ],
            default=self.__node_config__.query("children_class"),
            report=_report,
        )
        self.__node_children_class__ = _children_class

    def deepcopy(self):
        "Deep copy the container and its children"

        inst = super().deepcopy()

        if self.__node_children__ is not None:
            children = {}
            for key, val in self.__node_children__.items():
                children[key] = val.deepcopy()
            inst.__node_children__ = children

        return inst

    def set_default(self, *args):
        "Set default, accept one argument value"
        if len(args) == 1:
            value = args[0]
            value = super().set_default(value)
            self.__node__set_children__(value)
            return value

        assert False

    def set_value(self, *args):
        """Set value to object or to sub key.

        Usage:
          set_value(VALUE)
          set_value(KEY, VALUE)
        Args:
          key: The configuration key identifier
          value: The configuration value
        Returns:
          new_value: The new value
        """

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

    def __node__set_children__(self, value, mode="undefined"):
        "Set children"
        raise NotImplementedError("Subclass must implement this method")


class ConfigurationDict(_ContainerInstance):
    "Dict container configuration"

    # For dict
    __node_config__ = LeafContainerConfig(
        cast=as_dict,
        default=NOT_SET_DICT,
        help=None,
        children_class=Leaf,
    )

    def __node__set_children__(self, value, mode="update"):
        "Set children from dict"

        assert mode in ["define", "update"]

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
                "Instanciate ConfigurationDict child %s: %s(%s)",
                key,
                children_class.__name__,
                truncate(val),
            )

            child = children_class(parent=self, key=key, value=val)
            children[key] = child

        if mode == "define":
            self.__node_children__ = children
        elif mode == "update":
            self.__node_children__.update(children)
        else:
            assert False, f"Invalid mode {mode}"

    def get_children(self):
        "Get children as key/value dict"
        return self.__node_children__

    def get_child(self, key, noexceptions=False):
        "Get child from key name"
        ret = None
        if self.__node_children__ is not NOT_SET:
            ret = self.__node_children__.get(key, None)

        if ret is not None:
            return ret

        if noexceptions is True:
            return None
        msg = f"Child {key} not found in " f"{self.__node_fname__}"
        raise exceptions.UndeclaredField(msg)

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value of an key. Lookup children, or fallback on default or UNSET"

        if key is not None:
            return self.get_key_value(key, default=default, nodefaults=nodefaults)

        if self.__node_children__ is not NOT_SET:
            ret = {}
            for _key, child in self.__node_children__.items():
                ret[_key] = child.get_value(nodefaults=nodefaults)

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def get_key_value(self, key, default=UNSET_ARG, nodefaults=False):
        "Get parsed value for a given key (ask children first, then defaults or unset)"

        if self.__node_children__ is not NOT_SET:
            noexceptions = default != UNSET_ARG
            child = self.get_child(key, noexceptions=noexceptions)
            if child is None and default != UNSET_ARG:
                return default
            return child.get_value(default=default, nodefaults=nodefaults)

        if default == UNSET_ARG:
            default = super().get_default()

        return default.get(key, UNSET_ARG)

    def set_key_value(self, key, value):
        "Set key with value"
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
        "Iterator to loop over children as kee/value"
        return self.get_children().items()

    def values(self):
        "Return the value of all children only, no defaults"
        return self.get_children().values()

    def keys(self):
        "Return all children keys"
        return self.get_children().keys()

    def merge(self, other):
        "Merge container with other according to dict merge policy"

        if not isinstance(other, Leaf):
            raise ValueError("Cannot merge non-Leaf")

        strategy = getattr(self, "__node_merge__", MERGE_DICT_DEFAULT)
        logger.info(
            "Merge Container %s(%s) with %s(%s) strategy=%s",
            self.__class__.__name__,
            self.__node_fname__,
            other.__class__.__name__,
            other.__node_fname__,
            strategy,
        )

        merged_children = merge_maps(
            self.get_children(),
            other.get_children(),
            strategy,
            merge_both=lambda left, right: left.merge(right),
        )
        out = {key: child.get_value() for key, child in merged_children.items()}
        return type(self)(value=out, key=self.__node_key__)


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

        values_local = {}
        for attr, value in attrs.items():
            if isinstance(value, PublicField):
                values_local.update({attr: value})

        all_values = {**values, **values_local}
        attrs["__node_fields__"] = all_values

        # Clean attributes
        for key in list(all_values.keys()):
            if key in attrs:
                del attrs[key]

        return super(DeclarativeValuesMetaclass, mcs).__new__(
            mcs, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(mcs, *_):
        # Remember the order that values are defined.
        return OrderedDict()


class ConfigurationObj(ConfigurationDict, metaclass=DeclarativeValuesMetaclass):
    "Keyed dict container configuration"

    # For dict
    __node_config__ = LeafObjConfig(
        cast=as_dict,
        default=NOT_SET_DICT,
        help=None,
        extra_fields=False,
        children_class=Leaf,
        children_classes=NOT_SET_DICT,
    )

    def __node_init__(self, **kwargs):
        "Prepare ConfigurationObj instance"

        # Call parent init
        children_classes = kwargs.pop("children_classes", UNSET_ARG)
        super().__node_init__(**kwargs)
        _report = []

        # Fetch extra fields settings
        self.__node_extra_fields__ = self.__node_get_self_config__(
            "extra_fields",
            default=self.__node_config__.query("extra_fields"),
            report=_report,
        )

        # Fetch children_classes field settings
        local_values = self.__node_get_self_config__(
            "children_classes",
            default=self.__node_config__.query("children_classes"),
            overrides=[
                children_classes,
            ],
            report=_report,
        )
        assert isinstance(
            local_values, dict
        ), f"Expected a dict for {self.__node_fname__}, got: {type(local_values)}={local_values}"

        # Merge local fields with global fields
        _children_raw_classes = {}
        _children_raw_classes.update(self.__node_fields__)
        _children_raw_classes.update(
            local_values,
        )

        # Reprocess children fields
        _children_classes = []
        for attr, field in _children_raw_classes.items():

            if isinstance(field, GenericField):
                field.key = field.key if field.key else attr
                field.attr = attr
                _children_classes.append(field)
            else:
                raise TypeError(
                    f"Expected a GenericField for {attr}, got {type(field).__name__}"
                )

        self.__node_children_classes__ = _children_classes

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
            if extra_fields is not True:
                msg = (
                    f"Key '{child_key}' is not declared in "
                    f"'{self.__class__.__name__}({self.__node_fname__})', "
                    "use extra_fields=True to allow unknown keys"
                )
                if extra_fields == "warn":
                    logger.warning(msg)
                elif extra_fields is False:
                    raise exceptions.UndeclaredField(msg)
            child_field_cls = _children_class.__node_config__.__class__
            field = child_field_cls(key=key, attr=attr, instance_class=_children_class)

        # Check field result
        if not isinstance(field, GenericField):
            msg = (
                f"Expected a GenericField for {self.__node_fname__}.{child_key}, "
                f"got: {type(field)}={field}"
            )
            raise exceptions.InvalidField(msg)

        return field

    def __node__set_children__(self, value, mode="define"):
        "Set children"

        assert mode in ["define", "update"]

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
            if not inspect.isclass(child_cls):
                msg = (
                    f"Expected a class for {self.__node_fname__}.{child_key}, "
                    f"got: {type(child_cls)}={child_cls}"
                )
                assert False, msg

            # Build field default and value
            child_default = node_default_dict.get(
                child_key, child_field.query("default")
            )
            child_value = value.get(child_key, NOT_SET)

            logger.info(
                "Set child for ConfigurationObj %s(%s): %s",
                child_cls,
                self.__node_fname__,
                truncate(child_value),
            )

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

    # For list
    __node_config__ = LeafContainerConfig(
        cast=as_list,
        default=NOT_SET_LIST,
        help=None,
        children_class=Leaf,
        merge=MERGE_LIST_DEFAULT,
    )

    def merge(self, other):
        "Merge list container with other according to list merge policy"

        if not isinstance(other, Leaf):
            raise ValueError("Cannot merge non-Leaf")

        strategy = getattr(self, "__node_merge__", MERGE_LIST_DEFAULT)
        logger.info(
            "Merge List %s(%s) with %s(%s) strategy=%s",
            self.__class__.__name__,
            self.__node_fname__,
            other.__class__.__name__,
            other.__node_fname__,
            strategy,
        )

        self_val = self.get_value()
        other_val = other.get_value()
        base = self_val if isinstance(self_val, list) else []
        right = other_val if isinstance(other_val, list) else []
        return type(self)(
            value=merge_data(base, right, strategy, MergeKind.LIST),
            key=self.__node_key__,
        )

    def get_value(self, key=None, default=UNSET_ARG, nodefaults=False):
        "Get value"
        if key is not None:
            return self.get_key_value(key, nodefaults=nodefaults, default=default)

        if self.__node_children__ is not NOT_SET:
            ret = []
            for child in self.__node_children__.values():
                ret.append(child.get_value(nodefaults=nodefaults))

            return ret

        if default == UNSET_ARG:
            default = super().get_default()

        return default

    def __node__set_children__(self, value, mode="define"):
        "Set children from list"

        assert mode in ["define", "append", "replace"]

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
        offset = 0
        if mode == "append":
            offset = len(self.__node_children__)
        for index, val in enumerate(value):
            real_index = index + offset
            logger.info(
                "Instanciate ConfigurationList child %s: %s(%s)",
                real_index,
                children_class.__name__,
                truncate(val),
            )
            child = children_class(parent=self, key=real_index, value=val)
            children[real_index] = child

        if mode == "define":
            self.__node_children__ = children
        elif mode in ["append", "replace"]:
            self.__node_children__.update(children)
        else:
            assert False, f"Invalid mode {mode}"
