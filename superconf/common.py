"Common code"

# pylint: disable=too-few-public-methods
import json
import logging
import os

import yaml

log = logging.getLogger(__name__)


class _NoneType:
    """
    A special type that behaves as a replacement for None.
    We have to put a new default value to know if a variable has been set by
    the user explicitly. This is useful for the ``CommandLine`` loader, when
    CLI parsers force you to set a default value, and thus, break the discovery
    chain.
    """

    def repr(self):
        "Return string representation"
        return "<NONE_TYPE>"

    def __str__(self):
        return self.repr()

    def __repr__(self):
        return self.repr()

    def __bool__(self):
        return False


class NotSet(_NoneType):
    "Represent an unset arg"

    def repr(self):
        return "<NOT_SET>"

    @property
    def type(self):
        "Return object type"
        return self.__class__


class NotSetList(NotSet, list):
    "Represent an unset list"

    def repr(self):
        return "<NOT_SET_LIST>"


class NotSetDict(NotSet, dict):
    "Represent an unset dict"

    def repr(self):
        return "<NOT_SET_DICT>"


class UnSetArg(_NoneType):
    "Represent an unset arg"

    def repr(self):
        return "<UNSET_ARG>"


class Failure(_NoneType):
    "Represent a failure"

    def repr(self):
        return "<FAILURE>"


class Default(_NoneType):
    "Represent a default"

    def repr(self):
        return "<DEFAULT>"


NOT_SET = NotSet()
NOT_SET_LIST = NotSetList()
NOT_SET_DICT = NotSetDict()
UNSET_ARG = UnSetArg()
FAIL = UnSetArg()
DEFAULT = Default()
assert not NOT_SET
assert not NOT_SET_LIST
assert not NOT_SET_DICT
assert not UNSET_ARG
assert UNSET_ARG is not NOT_SET
assert NOT_SET is not UNSET_ARG
assert not isinstance(UNSET_ARG, str)
assert not isinstance(NOT_SET, str)
assert (NOT_SET or "INVALID") == "INVALID"

# assert UNSET_ARG is not NOT_SET
# assert UNSET_ARG == NOT_SET


def from_json(string):
    "Transform JSON string to python dict"
    return json.loads(string)


def to_json(obj, nice=True):
    "Transform JSON string to python dict"
    if nice:
        return json.dumps(obj, indent=2)
    return json.dumps(obj)


def from_yaml(string):
    "Transform YAML string to python dict"
    return yaml.safe_load(string)


def to_yaml(obj):
    "Transform obj to YAML"
    return yaml.dump(obj)

    # # Ruamel support
    # options = {}
    # string_stream = StringIO()

    # if isinstance(obj, str):
    #     obj = json.loads(obj)

    # yaml.dump(obj, string_stream, **options)
    # output_str = string_stream.getvalue()
    # string_stream.close()
    # if not headers:
    #     output_str = output_str.split("\n", 2)[2]
    # return output_str


def read_file(file):
    "Read file content"
    with open(file, encoding="utf-8") as _file:
        return "".join(_file.readlines())


def write_file(file, content, create_dirs=True):
    "Write content to file"

    if create_dirs:
        file_folder = os.path.dirname(file)
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)

    with open(file, "w", encoding="utf-8") as _file:
        _file.write(content)


# pylint: disable=redefined-builtin
def truncate(data, max=72, txt="..."):
    """Truncate a text to a maximum length.

    Args:
        data: The text to truncate
        max: Maximum length of the output text. If positive, truncates from end.
             If negative, truncates from start. If 0, returns original text.
        txt: Text to append/prepend to indicate truncation

    Returns:
        The truncated text string with txt added to indicate truncation
    """
    data = str(data)
    if max == 0:
        return data
    if len(data) > max:
        if max > 0:
            return data[: max + len(txt)] + txt
        return txt + data[(max - len(txt)) :]
    return data


# Source: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def unique(seq):
    "Remove duplicates from a list while preserving order"
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]
