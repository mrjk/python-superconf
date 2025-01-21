"Common code"


import json
import logging

import yaml

log = logging.getLogger(__name__)


class NotSet(str):
    """
    A special type that behaves as a replacement for None.
    We have to put a new default value to know if a variable has been set by
    the user explicitly. This is useful for the ``CommandLine`` loader, when
    CLI parsers force you to set a default value, and thus, break the discovery
    chain.
    """

    def repr(self):
        "Return string representation"
        return "<NOT_SET>"

    __str__ = repr
    __repr__ = repr


class UnSetArg(NotSet):
    "Represent an unset arg"

    def repr(self):
        return "<UNSET_ARG>"


class Failure(NotSet):
    "Represent a failure"

    def repr(self):
        return "<FAILURE>"


class Default(NotSet):
    "Represent a default"

    def repr(self):
        return "<DEFAULT>"


NOT_SET = NotSet()
UNSET_ARG = UnSetArg()
FAIL = UnSetArg()
DEFAULT = Default()
assert UNSET_ARG is not NOT_SET
# assert UNSET_ARG is not NOT_SET
# assert UNSET_ARG == NOT_SET


def from_json(string):
    "Transform JSON string to python dict"
    return json.loads(string)


def from_yaml(string):
    "Transform YAML string to python dict"
    return yaml.safe_load(string)


def read_file(file):
    "Read file content"
    with open(file, encoding="utf-8") as _file:
        return "".join(_file.readlines())
