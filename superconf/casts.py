"Support value casting"

# pylint: disable=too-few-public-methods

import ast
from collections.abc import Mapping, Sequence

from .common import FAIL  # , NOT_SET, UNSET_ARG
from .exceptions import InvalidCastConfiguration


class AbstractCast:
    """Base class for all cast operations.

    This abstract class defines the interface that all cast implementations must follow.
    Subclasses must implement the __call__ method to perform the actual casting operation.
    """

    def __call__(self, value):
        raise NotImplementedError()  # pragma: no cover


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
        # print (f"\n\n === PRINT CAST {value}===  \n")
        try:
            return self.values[str(value).lower()]
        except KeyError as err:
            raise InvalidCastConfiguration(
                f"Error casting value {value} to boolean"
            ) from err


class AsInt(AbstractCast):
    """Cast a value to an integer.

    Attempts to convert the input value to an integer using Python's built-in int() function.

    Raises:
        InvalidCastConfiguration: If the value cannot be converted to an integer.
    """

    def __call__(self, value):
        try:
            return int(value)
        except ValueError as err:
            # TOFIX: Raise or report unset ?
            # return NOT_SET
            raise InvalidCastConfiguration(
                f"Error casting value {value} to int"
            ) from err


class AsList(AbstractCast):
    """Cast a value to a list with support for delimited strings.

    Converts various input types to a list:
    - Empty values become empty lists
    - Strings are split by delimiter, with support for quoted elements
    - Sequences are converted directly to lists

    Args:
        delimiter (str, optional): The character used to split strings. Defaults to ','.
        quotes (str, optional): String containing valid quote characters. Defaults to '"\''.

    Examples:
        >>> cast = AsList()
        >>> cast('a,b,c')  # Returns: ['a', 'b', 'c']
        >>> cast('"a,b",c')  # Returns: ['a,b', 'c']
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

        if not value:
            # print ("PARSE AS EMPTY", value)
            return self.cast([])

        if isinstance(value, str):
            # print ("PARSE AS STRING", value)
            return self._parse_string(value)

        if isinstance(value, Sequence):
            # print ("PARSE AS LIST", value)
            return self.cast(value)
        if isinstance(value, Mapping):
            assert False, f"TOFIX: Unsupported type dict, {value}"

        assert False

    def _parse_string(self, string):
        elements = []
        element = []
        quote = ""
        for char in string:
            # open quote
            if char in self.quotes and not quote:
                quote = char
                element.append(char)
                continue

            # close quote
            if char in self.quotes and char == quote:
                quote = ""
                element.append(char)
                continue

            if quote:
                element.append(char)
                continue

            if char == self.delimiter:
                elements.append("".join(element))
                element = []
                continue

            element.append(char)

        # remaining element
        if element:
            elements.append("".join(element))

        return self.cast(e.strip() for e in elements)


class AsTuple(AsList):
    """Cast a value to a tuple.

    Inherits from AsList but converts the final result to a tuple instead of a list.
    Accepts the same arguments and follows the same parsing rules as AsList.

    Args:
        delimiter (str, optional): The character used to split strings. Defaults to ','.
        quotes (str, optional): String containing valid quote characters. Defaults to '"\''.
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

        if not value:
            # print ("PARSE AS EMPTY", value)
            return self.cast({})

        if isinstance(value, str):
            assert False, "String  parsing is not implemeted yet"
            # print ("PARSE AS STRING", value)
            # return self._parse_string(value)

        if isinstance(value, Mapping):
            # print ("PARSE AS LIST", value)
            return self.cast(value)
        if isinstance(value, Sequence):
            assert False, f"TOFIX: Unsupported type list, {value}"

        assert False


class AsOption(AbstractCast):
    """Cast a value by selecting from predefined options.

    Maps input values to predefined options using a dictionary mapping.
    Optionally supports a default option when the input doesn't match any defined option.

    Args:
        options (dict): A dictionary mapping input values to their corresponding options.
        default_option (any, optional): The key to use when the input value isn't found.
            If FAIL (default), raises an exception for invalid inputs.

    Raises:
        InvalidCastConfiguration: If the input value is not in options and no valid
            default_option is provided.

    Example:
        >>> cast = AsOption({'dev': ['debug'], 'prod': ['optimize']}, 'dev')
        >>> cast('prod')  # Returns: ['optimize']
        >>> cast('invalid')  # Returns: ['debug'] (default option)
    """

    def __init__(self, options, default_option=FAIL):
        self.options = options
        self.default_option = default_option

    def __call__(self, value):
        try:
            return self.options[value]
        except KeyError as err:

            # Raise error if no default
            default_option = self.default_option
            if default_option is FAIL:
                raise InvalidCastConfiguration(f"Invalid option {value}") from err

            # Look for default
            if not default_option in self.options:
                raise InvalidCastConfiguration(
                    f"Invalid default option {value}: does not exists: {default_option}"
                ) from err

            # if isinstance(default, str):
            return self.options[default_option]
            # if ret is NOT_SET:
            #     raise InvalidCastConfiguration("Invalid default option {!r}".format(value))

            # return ret


class AsIdentity(AbstractCast):
    """Return the input value unchanged.

    A no-operation cast that simply returns the input value without modification.
    Useful as a default cast or when you need to maintain the original type.
    """

    def __call__(self, value):
        return value


evaluate = ast.literal_eval
