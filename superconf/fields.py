"Fields management"

# pylint: disable=protected-access
# pylint: disable=invalid-name

import logging

from superconf import exceptions
from superconf.casts import (
    as_boolean,
    as_dict,
    as_int,
    as_list,
    as_tuple,
)
from superconf.common import MERGE_DICT_DEFAULT, MERGE_LIST_DEFAULT, NOT_SET
from superconf.configuration import (
    Leaf,
    PublicField,
)

logger = logging.getLogger(__name__)


# ====================================
# Base Fields
# ====================================


class FieldContainer(PublicField):
    "Represent a configuration container field."

    instance_class = Leaf

    def get_keys(self):
        "Get keys"
        out = list(self.__field_default__.keys())
        out.extend(list(self.__field_override__.keys()))
        return out

    def dump(self):
        "Dump the field"
        out = {}
        out.update(self.__field_default__)
        out.update(self.__field_override__)
        return out

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
        node_field = self.instance_class.__node_config__

        # Validate kwargs and report unknown fields
        overrides = {}
        field_names = node_field.get_keys()
        for key, val in kwargs.items():
            if key not in field_names:
                msg = f"Unknown field: {key}={val} for Field '{node_field}'"
                raise exceptions.InvalidFieldOption(msg)

            overrides[key] = val

        # Fetch base config from Field class attributes
        defaults = {}
        for name in field_names:
            if hasattr(self, name):
                val = getattr(self, name)
                defaults[name] = val

        self.__field_default__ = defaults
        self.__field_override__ = overrides

    def query(self, name, default=NOT_SET):
        "Get a configuration value"

        # Return overrided args from init
        if name in self.__field_override__:
            return self.__field_override__[name]

        # Return default args from class
        if name in self.__field_default__:
            return self.__field_default__[name]

        return default


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


# class FieldOption(FieldLeaf):
#     """A field that validates values against a predefined set of options.

#     This field ensures that values are one of a predefined set of options,
#     optionally providing a default if an invalid option is given.

#     Attributes:
#         cast: Set to AsOption for option validation and conversion.
#     """

#     cast = as_option

#     def __init__(
#         self,
#         options,
#         default_option=FAIL,
#         key: str = None,
#         **kwargs,
#     ):
#         """Initialize an option field.

#         Args:
#             options: Dictionary mapping valid input values to their corresponding options.
#             default_option: The option to use when an invalid value is provided.
#                 If set to FAIL, raises an error for invalid values.
#             key: Name of the value used in file or environment variable.
#             **kwargs: Additional arguments passed to the parent Field class.

#         Raises:
#             AssertionError: If options is not a dictionary.
#         """
#         assert isinstance(options, dict), f"Expected a dict, got: {options}"
#         self.cast = AsOption(options, default_option=default_option)
#         super().__init__(key, **kwargs)


class FieldDict(FieldLeaf):
    """A field that stores dictionary values.

    Uses the AsDict cast to ensure values are proper dictionaries,
    with support for converting mapping objects.

    Attributes:
        cast: Set to AsDict() for automatic type conversion.
        merge: Default dict merge strategy (``override``).
    """

    cast = as_dict
    merge = MERGE_DICT_DEFAULT


class FieldList(FieldLeaf):
    """A field that stores list values.

    Uses the AsList cast to convert various inputs to lists, including:
    - Comma-separated strings
    - Other sequence types
    - Empty values to empty lists

    Attributes:
        cast: Set to AsList() for automatic type conversion.
        merge: Default list merge strategy (``append``).
    """

    cast = as_list
    merge = MERGE_LIST_DEFAULT


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
