"Support value casting"

# pylint: disable=too-few-public-methods, too-many-return-statements

import ast
import logging
from collections.abc import Mapping, Sequence

from superconf.common import NOT_SET, NOT_SET_DICT, NOT_SET_LIST, is_not_set
from superconf.exceptions import InvalidCastConfiguration

logger = logging.getLogger(__name__)


class AbstractCast:
    """Base class for all cast operations.

    This abstract class defines the interface that all cast implementations must follow.
    Subclasses must implement the __call__ method to perform the actual casting operation.
    """

    def __call__(self, value):
        raise NotImplementedError()  # pragma: no cover

    def __json_dump__(self):
        return self.__dict__


class AsBoolean(AbstractCast):
    """Cast a value to a boolean using predefined string mappings.

    Converts various string representations to boolean values using a configurable
    mapping dictionary. By default, supports common boolean string representations
    like 'true', 'yes', 'on', '1' for True and their counterparts for False.

    Args:
        values (dict, optional): A dictionary mapping strings to boolean values.
            If provided, updates the default mapping dictionary.

    Raises:
        InvalidCastConfiguration: If the input value cannot be cast to a boolean.
    """

    default_values = {
        "1": True,
        "true": True,
        "yes": True,
        "y": True,
        "on": True,
        "t": True,
        "0": False,
        "false": False,
        "no": False,
        "n": False,
        "off": False,
        "f": False,
    }

    def __init__(self, values=None):
        self.values = self.default_values.copy()
        if isinstance(values, dict):
            self.values.update(values)

    def __call__(self, value):
        try:
            return self.values[str(value).lower()]
        except KeyError as err:
            raise InvalidCastConfiguration(
                f"Error casting value {value} to boolean"
            ) from err


class AsString(AbstractCast):
    """Cast a value to a string.

    Attempts to convert the input value to a string using Python's built-in str() function.

    Raises:
        InvalidCastConfiguration: If the value cannot be converted to a string.
    """

    def __call__(self, value):
        if isinstance(value, str):
            return str(value)
        if not value:
            return ""
        return str(value)


class AsInt(AbstractCast):
    """Cast a value to an integer.

    Attempts to convert the input value to an integer using Python's built-in int() function.

    Raises:
        InvalidCastConfiguration: If the value cannot be converted to an integer.
    """

    def __call__(self, value):
        try:
            return int(value)
        except (ValueError, TypeError) as err:
            raise InvalidCastConfiguration(
                f"Error casting value {value} to int"
            ) from err


class AsList(AbstractCast):
    """Cast a value to a list.

    Converts various input types to a list:
    - ``None`` / ``NOT_SET`` become ``NOT_SET_LIST``
    - Scalars (``str``, ``int``, ``float``, ``bool``) are wrapped in a one-element list
    - Sequences are converted with ``list(...)``

    Args:
        delimiter (str, optional): Reserved for callers/subclasses. Defaults to ','.
        quotes (str, optional): Reserved for callers/subclasses. Defaults to '"\''.

    Examples:
        >>> cast = AsList()
        >>> cast('a,b,c')  # Returns: ['a,b,c']
        >>> cast(['a', 'b'])  # Returns: ['a', 'b']
    """

    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes

    def cast(self, sequence):
        "Cast to correct type"
        return list(sequence)

    def __call__(self, value):
        return self._parse(value)

    def _parse(self, value):

        if is_not_set(value):
            assert value is NOT_SET_LIST or value is NOT_SET
            return NOT_SET_LIST

        if value is None:
            return NOT_SET_LIST

        if isinstance(value, (str, int, float, bool)):
            logger.info("Embed %s value into list: [%s]", type(value), value)
            value = [value]

        if isinstance(value, Sequence):  # and not isinstance(value, str):
            return self.cast(value)
        if isinstance(value, Mapping):
            raise InvalidCastConfiguration(
                f"Cannot cast mapping value '{value}' to list"
            )

        raise InvalidCastConfiguration(f"Error casting value '{value}' to list")


class AsTuple(AsList):
    """Cast a value to a tuple.

    Inherits from AsList but converts the final result to a tuple instead of a list.
    Accepts the same arguments and follows the same parsing rules as AsList.

    Args:
        delimiter (str, optional): Reserved for callers/subclasses. Defaults to ','.
        quotes (str, optional): Reserved for callers/subclasses. Defaults to '"\''.
    """

    def cast(self, sequence):
        return tuple(sequence)


class AsDict(AbstractCast):
    """Cast a value to a dictionary.

    Currently supports:
    - Empty values become empty dictionaries
    - Mapping objects are converted directly to dictionaries

    Args:
        delimiter (str, optional): Reserved for future string parsing. Defaults to ','.
        quotes (str, optional): Reserved for future string parsing. Defaults to '"\''.

    Note:
        String parsing is not yet implemented.
    """

    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes

    def cast(self, sequence):
        "Cast value"
        return dict(sequence)

    def __call__(self, value):
        return self._parse(value)

    def _parse(self, value):
        "Internal helper to parse values"

        if is_not_set(value):
            assert value is NOT_SET_DICT or value is NOT_SET
            return NOT_SET_DICT

        if value is None:
            return NOT_SET_DICT

        if isinstance(value, (str, int, float, bool)):
            raise InvalidCastConfiguration(
                f"Error casting invalid type string '{value}' to dict"
            )

        if isinstance(value, Mapping):
            return self.cast(value)

        if isinstance(value, Sequence):
            # Support for dict defined as list of single key/value
            out = {}
            for val in value:
                if isinstance(val, str):
                    # Just a key
                    out[val] = None
                elif isinstance(val, dict):
                    # If it's a dict, ensure it have only one key
                    key_count = len(val)
                    assert key_count == 1
                    key = list(val.keys())[0]
                    out[key] = val[key]
                else:
                    raise InvalidCastConfiguration(
                        f"Cannot cast sequence item '{val}' to a dictionary entry"
                    )

            return self.cast(out)

        raise InvalidCastConfiguration(f"Error casting value '{value}' to dict")


# class AsOption(AbstractCast):
#     """Cast a value by selecting from predefined options.

#     Maps input values to predefined options using a dictionary mapping.
#     Optionally supports a default option when the input doesn't match any defined option.

#     Args:
#         options (dict): A dictionary mapping input values to their corresponding options.
#         default_option (any, optional): The key to use when the input value isn't found.
#             If FAIL (default), raises an exception for invalid inputs.

#     Raises:
#         InvalidCastConfiguration: If the input value is not in options and no valid
#             default_option is provided.

#     Example:
#         >>> cast = AsOption({'dev': ['debug'], 'prod': ['optimize']}, 'dev')
#         >>> cast('prod')  # Returns: ['optimize']
#         >>> cast('invalid')  # Returns: ['debug'] (default option)
#     """

#     def __init__(self, options, default_option=FAIL):
#         self.options = options
#         self.default_option = default_option

#     def __call__(self, value):
#         try:
#             return self.options[value]
#         except KeyError as err:

#             # Raise error if no default
#             default_option = self.default_option
#             if default_option is FAIL:
#                 raise InvalidCastConfiguration(f"Invalid option {value}") from err

#             # Look for default
#             if not default_option in self.options:
#                 raise InvalidCastConfiguration(
#                     f"Invalid default option {value}: does not exists: {default_option}"
#                 ) from err

#             # if isinstance(default, str):
#             return self.options[default_option]
#             # if ret is NOT_SET:
#             #     raise InvalidCastConfiguration("Invalid default option {!r}".format(value))

#             # return ret


class AsIdentity(AbstractCast):
    """Return the input value unchanged.

    A no-operation cast that simply returns the input value without modification.
    Useful as a default cast or when you need to maintain the original type.
    """

    def __call__(self, value):
        return value


class AsBest(AbstractCast):
    """Cast a value to its most appropriate Python type.

    Attempts to intelligently determine and convert the input value to the most
    suitable Python type by trying different conversions in order:
    1. None for null/empty values
    2. Boolean for true/false-like strings
    3. Integer for numeric strings without decimals
    4. Float for numeric strings with decimals
    5. List for comma-separated strings or sequence-like inputs
    6. Dict for mapping-like inputs
    7. Original string if no other conversion succeeds

    Examples:
        >>> cast = AsBest()
        >>> cast('123')  # Returns: 123 (int)
        >>> cast('3.14')  # Returns: 3.14 (float)
        >>> cast('true')  # Returns: True (bool)
        >>> cast('a,b,c')  # Returns: ['a', 'b', 'c'] (list)
    """

    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.list_caster = AsList(delimiter=delimiter, quotes=quotes)
        self.dict_caster = AsDict(delimiter=delimiter, quotes=quotes)

    def __call__(self, value):
        if not value:
            return None

        # Try boolean first for true/false strings
        if isinstance(value, str):

            # Try integer
            try:
                if "." not in value:
                    return int(value)
            except ValueError:
                pass

            # Try float
            try:
                return float(value)
            except ValueError:
                pass

            # Try list (if contains delimiter)
            if self.delimiter and self.delimiter in value:
                try:
                    return self.list_caster(value)
                except (InvalidCastConfiguration, AssertionError):
                    pass

        # Try dict for mapping types
        if isinstance(value, Mapping):
            try:
                return self.dict_caster(value)
            except (InvalidCastConfiguration, AssertionError):
                pass

        # Try list for sequence types
        if isinstance(value, Sequence) and not isinstance(value, str):
            try:
                return self.list_caster(value)
            except (InvalidCastConfiguration, AssertionError):
                pass

        # Return as is if no conversion succeeded
        return value


evaluate = ast.literal_eval


# Shortcuts for standard casts
as_string = AsString()
as_boolean = AsBoolean()
as_int = AsInt()
as_list = AsList()
as_dict = AsDict()
as_tuple = AsTuple()
# as_option = AsOption()
as_is = AsIdentity()
