"Fields management"

# pylint: disable=protected-access

# TOFIX:
# pylint: disable=invalid-name


# from pprint import pprint
import logging

from superconf import exceptions

# from superconf import exceptions
from superconf.casts import (  # as_string,
    as_boolean,
    as_dict,
    as_int,
    as_is,
    as_list,
    as_option,
    as_tuple,
)
from superconf.common import FAIL, NOT_SET, UNSET_ARG
from superconf.configuration import (
    Leaf,
    PublicField,
)

logger = logging.getLogger(__name__)


# ====================================
# Base Fields
# ====================================


class FieldContainer(PublicField):
    "Represent a configuration class WIP/BROKEN"

    instance_class = Leaf

    def __init__(
        self,
        instance_class,
        **kwargs,
    ):

        # Fetch instance class
        self.instance_class = instance_class or self.instance_class
        assert issubclass(
            self.instance_class, Leaf
        ), f"Expected a Leaf for {self}, got: {type(self.instance_class)}={self.instance_class}"

        # Fetch node field
        node_field = self.instance_class.tmp__node_config

        # Validate kwargs and report unknown fields
        field_names = node_field.get_keys()
        for key, val in kwargs.items():
            if key not in field_names:
                msg = f"Unknown field: {key}={val} for Field '{node_field}'"
                raise exceptions.InvalidFieldOption(msg)

        # Fetch base config
        base_cfg = {}
        for name in field_names:
            if hasattr(self, name):
                val = getattr(self, name)
                base_cfg[name] = val

        # Build requested config
        new_cfg = {}
        new_cfg.update(node_field.dump())
        new_cfg.update(base_cfg)
        new_cfg.update(kwargs)

        # Apply config attributes
        for key, val in new_cfg.items():
            setattr(self, key, val)


class FieldLeaf(FieldContainer):
    "Represent a configuration leaf"

    def __init__(self, instance_class=None, **kwargs):

        super().__init__(instance_class, **kwargs)


Field = FieldLeaf


# Leaf Fields
# ============================


class FieldBool(FieldLeaf):
    """A field that stores and validates boolean values.

    Uses the AsBoolean cast to convert various string representations
    to boolean values (e.g., 'yes'/'no', 'true'/'false', '1'/'0').

    Attributes:
        cast: Set to AsBoolean() for automatic type conversion.
    """

    cast = as_boolean


class FieldString(FieldLeaf):
    """A field that stores string values.

    Ensures values are stored as strings, converting other types
    if necessary using Python's built-in str() function.

    Attributes:
        cast: Set to str for automatic type conversion.
    """

    cast = str


class FieldInt(FieldLeaf):
    """A field that stores integer values.

    Uses the AsInt cast to convert string representations to integers,
    raising an error if the conversion fails.

    Attributes:
        cast: Set to AsInt() for automatic type conversion.
    """

    cast = as_int


class FieldFloat(FieldLeaf):
    """A field that stores floating-point values.

    Uses Python's built-in float() function to convert values,
    raising an error if the conversion fails.

    Attributes:
        cast: Set to float for automatic type conversion.
    """

    cast = float


class FieldOption(FieldLeaf):
    """A field that validates values against a predefined set of options.

    This field ensures that values are one of a predefined set of options,
    optionally providing a default if an invalid option is given.

    Attributes:
        cast: Set to AsOption for option validation and conversion.
    """

    cast = as_option

    def __init__(
        self,
        options,
        default_option=FAIL,
        key: str = None,
        **kwargs,
    ):
        """Initialize an option field.

        Args:
            options: Dictionary mapping valid input values to their corresponding options.
            default_option: The option to use when an invalid value is provided.
                If set to FAIL, raises an error for invalid values.
            key: Name of the value used in file or environment variable.
            **kwargs: Additional arguments passed to the parent Field class.

        Raises:
            AssertionError: If options is not a dictionary.
        """
        assert isinstance(options, dict), f"Expected a dict, got: {options}"
        self.cast = AsOption(options, default_option=default_option)
        super().__init__(key, **kwargs)


class FieldDict(FieldLeaf):
    """A field that stores dictionary values.

    Uses the AsDict cast to ensure values are proper dictionaries,
    with support for converting mapping objects.

    Attributes:
        cast: Set to AsDict() for automatic type conversion.
    """

    cast = as_dict


class FieldList(FieldLeaf):
    """A field that stores list values.

    Uses the AsList cast to convert various inputs to lists, including:
    - Comma-separated strings
    - Other sequence types
    - Empty values to empty lists

    Attributes:
        cast: Set to AsList() for automatic type conversion.
    """

    cast = as_list


class FieldTuple(FieldLeaf):
    """A field that stores tuple values.

    Uses the AsTuple cast to convert various inputs to tuples, including:
    - Comma-separated strings
    - Other sequence types
    - Empty values to empty tuples

    Attributes:
        cast: Set to AsTuple() for automatic type conversion.
    """

    cast = as_tuple


# Container Fields
# ============================


class FieldConf(FieldContainer):
    """A field that represents a nested configuration.

    This field type allows for hierarchical configuration structures by containing
    another configuration class as its value.

    """
