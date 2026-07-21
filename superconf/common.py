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
    is_not_set,
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
assert isinstance(NOT_SET_DICT, NOT_SET_DICT.type)
assert isinstance(NOT_SET_DICT, NOT_SET.type) or NOT_SET_DICT is NOT_SET


def from_json(string):
    "Transform JSON string to python dict"
    return json.loads(string)


class CustomJSONEncoder(json.JSONEncoder):
    """
    Custom JSON encoder to handle specific object types.
    This method is called for objects not natively JSON serializable.
    """

    # pylint: disable=arguments-renamed
    def default(self, obj):
        """
        Custom JSON encoder to handle specific object types.
        This method is called for objects not natively JSON serializable.
        """

        if hasattr(obj, "__json_dump__"):
            return obj.__json_dump__()

        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def to_json(obj, nice=True):
    "Transform JSON string to python dict"
    if nice:
        return json.dumps(obj, indent=2, cls=CustomJSONEncoder)
    return json.dumps(obj, cls=CustomJSONEncoder)


def from_yaml(string):
    "Transform YAML string to python dict"
    return yaml.safe_load(string)


def to_yaml(obj):
    "Transform obj to YAML"
    return yaml.dump(obj)


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


# pylint: disable=line-too-long
# Source: https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def unique(seq):
    "Remove duplicates from a list while preserving order"
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


# Re-export merge API (implementation lives in merge.py)
from superconf.merge import (  # noqa: E402  pylint: disable=wrong-import-position
    MERGE_APPEND,
    MERGE_DICT_DEFAULT,
    MERGE_DICT_STRATEGIES,
    MERGE_KEEP,
    MERGE_LIST_DEFAULT,
    MERGE_LIST_STRATEGIES,
    MERGE_OTHER_DEFAULT,
    MERGE_OTHER_STRATEGIES,
    MERGE_OVERRIDE,
    MERGE_OVERRIDE_ABSENT,
    MERGE_OVERRIDE_NON_NULL,
    MERGE_OVERRIDE_PRESENT,
    MERGE_PREPEND,
    MERGE_REPLACE,
    MergeKind,
    MergeStrategy,
    ensure_merge_strategy,
    infer_merge_kind,
    is_merge_value_set,
    merge_data,
    merge_dict_data,
    merge_list_data,
    merge_maps,
    normalize_merge_strategy,
    prefer_other_scalar,
)
