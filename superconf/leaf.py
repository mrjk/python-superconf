"""Leaf configuration models."""

import logging
from typing import Any, Optional, Union

from superconf import exceptions
from superconf.casts import as_is
from superconf.common import (
    MERGE_DICT_DEFAULT,
    MERGE_OTHER_DEFAULT,
    NOT_SET,
    NOT_SET_DICT,
    UNSET_ARG,
    infer_merge_kind,
    is_merge_value_set,
    is_not_set,
    merge_data,
    normalize_merge_strategy,
    prefer_other_scalar,
)
from superconf.merge import MergeKind
from superconf.nodes import Node

logger = logging.getLogger(__name__)

# ====================================
# Base Fields V2
# ====================================


class GenericField:
    "Generic field"

    key = None
    instance_class = None

    def __repr__(self):
        key_list = ",".join(list(self.__dict__.keys()))
        if hasattr(self, "get_keys"):
            key_list = self.dump()
            key_list = f"{key_list}"
        return f"Field({self.__class__.__name__}) at {hex(id(self))}: {key_list}"

    def __bool__(self):
        return True

    def dump(self):
        "Dump the configuration"
        return dict(self.__dict__)

    def query(self, name, default=NOT_SET):
        "Get a configuration value"
        return getattr(self, name, default)

    def __json_dump__(self):
        return self.__dict__


class PublicField(GenericField):
    "Public field"


# LeafBaseConfig
class LeafBaseConfig(GenericField):
    "Represent a configuration leaf"

    def get_keys(self):
        "Get class item"
        return list(self.__dict__.keys())

    # pylint: disable=redefined-builtin, too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        default=NOT_SET,
        help=NOT_SET,
        cast=NOT_SET,
        instance_class=NOT_SET,
        attr=NOT_SET,
        key=NOT_SET,
        merge=MERGE_OTHER_DEFAULT,
    ):

        self.key = key
        self.default = default
        self.help = help
        self.cast = cast
        self.instance_class = instance_class
        self.attr = attr
        self.merge = merge


# LeafContainerConfig
class LeafContainerConfig(LeafBaseConfig):
    "Represent a Configuration Container leaf"

    def __init__(
        self,
        children_class=NOT_SET,
        merge=MERGE_DICT_DEFAULT,
        **kwargs,
    ):

        self.children_class = children_class
        super().__init__(merge=merge, **kwargs)


# LeafObjConfig
class LeafObjConfig(LeafContainerConfig):
    "Represent a Configuration Object leaf"

    def __init__(
        self,
        extra_fields=NOT_SET,
        children_classes=NOT_SET_DICT,
        **kwargs,
    ):

        self.extra_fields = extra_fields
        self.children_classes = children_classes
        super().__init__(**kwargs)


# ====================================
# Helpers
# ====================================


def node_cast_value(self, value):
    "Cast value"

    def _cast(value):
        # If there is no cast callable, then return directly the value
        if self.__node_cast__ is None or self.__node_cast__ is NOT_SET:
            return value

        # Otherwise, try to cast the value
        try:
            value = self.__node_cast__(value)
        except Exception as err:
            raise exceptions.InvalidCastConfiguration(
                f"Invalid cast {self.__node_cast__} for {self.__node_fname__} "
                f"for value: {value}, got error: {type(err).__name__} {err}"
            )

        return value

    new_val = _cast(value)
    if new_val != value:
        msg = f"Cast value {self.__node_fname__} with {self.__node_cast__}: {value} -> {new_val}"
        logger.debug(msg)

    return new_val


# ====================================
# Configuration Child
# ====================================


class Leaf(Node):
    "Leaf instance, representing a value"

    __node_config__ = LeafBaseConfig(
        cast=as_is,
        default=NOT_SET,
        help=None,
    )

    __node_value__ = NOT_SET
    __node_default__ = NOT_SET
    __node_cast__ = None
    __node_field__ = None

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        value: Any = NOT_SET,
        default=UNSET_ARG,
        key: Optional[Union[str, int]] = None,
        parent: Optional["Node"] = None,
        field=None,
        **kwargs,
    ):
        super().__init__(key=key, value=value, parent=parent)

        # Get default and override node field
        self.__node_field__ = GenericField() if field is None else field
        assert isinstance(
            self.__node_field__, GenericField
        ), f"Invalid __node_field__ type: {self.__node_field__}"
        assert isinstance(
            self.__node_config__, LeafBaseConfig
        ), f"Invalid __node_config__ type: {self.__node_config__.__class__.__mro__}"

        # Validate override Meta
        metadata = getattr(self, "Meta", None)
        if metadata is not None:
            for _key, _ in metadata.__dict__.items():
                if _key.startswith("__"):
                    continue
                if not hasattr(self.__node_config__, _key):
                    msg = (
                        f"Invalid Meta key '{_key}' for {self.__class__}, "
                        f"please choose one of: {list(self.__node_config__.__dict__.keys())}"
                    )
                    raise exceptions.InvalidField(msg)

        # Call node init hook
        self.__node_init__(**kwargs)

        _report = []
        _default = self.__node_get_self_config__(
            "default",
            default=self.__node_config__.default,
            overrides=[
                default,
                self.__node_field__.query("default"),
            ],
            report=_report,
        )

        # Set default value
        self.set_default(_default)

        # Set value if present
        if value is not UNSET_ARG and not is_not_set(value):
            self.set_value(value)

        # Run post_load hook
        self.post_load()

    def __node_init__(self, **kwargs):
        "Prepare Leaf instance"

        # Call parent init
        cast = kwargs.pop("cast", UNSET_ARG)
        assert len(kwargs) == 0, f"Unexpected kwargs: {kwargs}"
        _report = []

        # Fetch cast settings
        _cast = self.__node_get_self_config__(
            "cast",
            default=self.__node_config__.query("cast"),
            overrides=[
                cast,
                self.__node_field__.query("cast"),
            ],
            report=_report,
        )
        self.__node_cast__ = _cast

        # Fetch merge policy (Field override > Meta > config default)
        _merge = self.__node_get_self_config__(
            "merge",
            default=self.__node_config__.query("merge"),
            overrides=[
                self.__node_field__.query("merge"),
            ],
            report=_report,
        )
        self.__node_merge__ = normalize_merge_strategy(_merge)

    def __repr__(self):
        "Represent the instance"
        return f"{self.__class__.__name__}({self.__node_key__}) at {hex(id(self))}"

    def _apply_casted(self, value, attr_name: str, debug_label: str):
        """Pre-load, cast, store on ``attr_name``, and log.

        Args:
            value: Raw value to store.
            attr_name: Instance attribute that holds the casted value.
            debug_label: Short label for the debug log message.

        Returns:
            The casted value that was stored.
        """
        value = self.pre_load(value)
        value = node_cast_value(self, value)
        setattr(self, attr_name, value)
        logger.debug(
            "Set %s for %s: %s",
            debug_label,
            self.__node_fname__,
            getattr(self, attr_name),
        )
        return getattr(self, attr_name)

    def set_default(self, value):
        "Set default value"
        return self._apply_casted(value, "__node_default__", "default")

    def set_value(self, value):
        "Set value"
        return self._apply_casted(value, "__node_value__", "value")

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

    @property
    def __node_help__(self) -> str:
        "Get leaf help message"

        ret = self.__node_field__.query("help", NOT_SET)
        if ret != NOT_SET:
            return ret

        return self.__doc__ or "<NO_HELP>"

    def _merge_strategy_for(self, other, default_strategy):
        """Validate merge peer and return this node's merge strategy.

        Args:
            other: Peer node to merge with.
            default_strategy: Fallback when ``__node_merge__`` is unset.

        Returns:
            Resolved merge strategy.

        Raises:
            ValueError: If ``other`` is not a Leaf.
        """
        if not isinstance(other, Leaf):
            raise ValueError("Cannot merge non-Leaf")
        return getattr(self, "__node_merge__", default_strategy)

    def merge(self, other):
        "Merge and override object with other according to merge policy"

        strategy = self._merge_strategy_for(other, MERGE_OTHER_DEFAULT)
        self_val = self.get_value(nodefaults=True)
        other_val = other.get_value(nodefaults=True)
        kind = infer_merge_kind(
            strategy,
            self_val if is_merge_value_set(self_val) else None,
            other_val if is_merge_value_set(other_val) else None,
        )

        logger.info(
            "Merge Leaf %s(%s) with %s(%s) strategy=%s kind=%s",
            self.__class__.__name__,
            self.__node_fname__,
            other.__class__.__name__,
            other.__node_fname__,
            strategy,
            kind,
        )

        if kind in (MergeKind.LIST, MergeKind.DICT):
            empty = [] if kind == MergeKind.LIST else {}
            base = self_val if is_merge_value_set(self_val) else empty
            right = other_val if is_merge_value_set(other_val) else empty
            expected = list if kind == MergeKind.LIST else dict
            if not isinstance(base, expected) or not isinstance(right, expected):
                raise ValueError(
                    f"{kind.value} merge on {self.__node_fname__} requires "
                    f"{expected.__name__} values, got: {type(base)} and {type(right)}"
                )
            inst = self.copy()
            inst.set_value(merge_data(base, right, strategy, kind))
            return inst

        if prefer_other_scalar(self_val, other_val, strategy):
            return other
        return self

    def copy(self):
        "Copy the instance"

        curr = self.__dict__.copy()
        curr_default = curr.pop("__node_default__", None)
        curr_value = curr.pop("__node_value__", None)
        curr_key = curr.pop("__node_key__", None)
        curr_parent = curr.pop("__node_parent__", None)

        # Instanciate copy
        inst = self.__class__(
            key=curr_key, default=curr_default, value=curr_value, parent=curr_parent
        )
        inst.__dict__.update(curr)
        return inst

    def deepcopy(self):
        "Copy the instance"
        return self.copy()
