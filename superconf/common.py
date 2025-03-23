"Common code"

# pylint: disable=too-few-public-methods
import json
import logging
import os

import yaml

# pylint: disable=unused-import
from superconf.lib.sentinel_v2 import (
    DEFAULT,
    FAIL,
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    UNSET_ARG,
)

log = logging.getLogger(__name__)

assert not NOT_SET
assert not NOT_SET_LIST
assert not NOT_SET_DICT
assert not UNSET_ARG
assert UNSET_ARG is not NOT_SET
assert NOT_SET is not UNSET_ARG
assert not isinstance(UNSET_ARG, str)
assert not isinstance(NOT_SET, str)
assert (NOT_SET or "INVALID") == "INVALID"
assert isinstance(NOT_SET_DICT, dict)
assert isinstance(NOT_SET_LIST, list)
assert isinstance(NOT_SET_DICT, NOT_SET.type)
assert NOT_SET_DICT is NOT_SET_DICT or NOT_SET_DICT is NOT_SET


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
