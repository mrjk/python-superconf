import ast

from .exceptions import InvalidCastConfiguration
from .common import NOT_SET, UNSET_ARG, FAIL
from collections.abc import Mapping, Sequence

class AbstractCast(object):
    def __call__(self, value):
        raise NotImplementedError()  # pragma: no cover


class AsBoolean(AbstractCast):
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
        except KeyError:
            raise InvalidCastConfiguration(
                "Error casting value {!r} to boolean".format(value)
            )

class AsInt(AbstractCast):
    "Return an INT"

    def __call__(self, value):
        try:
            return int(value)
        except ValueError:
            # TOFIX: Raise or report unset ?
            return NOT_SET
            raise InvalidCastConfiguration(
                "Error casting value {!r} to int".format(value)
            )

class AsList(AbstractCast):
    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes


    def cast(self, sequence):
        return list(sequence)

    def __call__(self, value):
        return self._parse(value)


    def _parse(self, value):
        
        if not value:
            # print ("PARSE AS EMPTY", value)
            return self.cast([])
        elif isinstance(value, str):
            # print ("PARSE AS STRING", value)
            return self._parse_string(value)
        
        elif isinstance(value, Sequence):
            # print ("PARSE AS LIST", value)
            return self.cast(value)
        elif isinstance(value, Mapping):
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
    def cast(self, sequence):
        return tuple(sequence)



class AsDict(AbstractCast):

    def __init__(self, delimiter=",", quotes="\"'"):
        self.delimiter = delimiter
        self.quotes = quotes

    def cast(self, sequence):
        return dict(sequence)

    def __call__(self, value):
        return self._parse(value)


    def _parse(self, value):
        
        if not value:
            # print ("PARSE AS EMPTY", value)
            return self.cast({})
        elif isinstance(value, str):
            assert False, "String  parsing is not implemeted yet"
            # print ("PARSE AS STRING", value)
            return self._parse_string(value)
        
        elif isinstance(value, Mapping):
            # print ("PARSE AS LIST", value)
            return self.cast(value)
        elif isinstance(value, Sequence):
            assert False, f"TOFIX: Unsupported type list, {value}"

        assert False


class AsOption(AbstractCast):
    """
    Example::
        _INSTALLED_APPS = ("foo", "bar")
        INSTALLED_APPS = config("ENVIRONMENT", default="production", cast=Option({
            "production": _INSTALLED_APPS,
            "local": _INSTALLED_APPS + ("baz",)
        }))
    """

    def __init__(self, options, default_option=FAIL):
        self.options = options
        self.default_option = default_option

    def __call__(self, value):
        try:
            return self.options[value]
        except KeyError:

            # Raise error if no default
            default_option = self.default_option
            if default_option is FAIL:
                raise InvalidCastConfiguration("Invalid option {!r}".format(value))
            
            # Look for default
            if not default_option in self.options:
                raise InvalidCastConfiguration("Invalid default option {!r}: does not exists: {}".format(value, default_option))

            # if isinstance(default, str):
            return self.options[default_option]
            # if ret is NOT_SET:
            #     raise InvalidCastConfiguration("Invalid default option {!r}".format(value))

            # return ret


class AsIdentity(AbstractCast):
    """
    This is basically the no-op cast
    """

    def __call__(self, value):
        return value


evaluate = ast.literal_eval
