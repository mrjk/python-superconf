"""Sentinel value implementation for representing special states.

This module provides sentinel objects that represent special states like "not set" or
"unset argument". Sentinels are singleton objects that can be used to indicate
special conditions in a more explicit way than using None.

Key features:
- Singleton pattern implementation
- Type-specific sentinel objects (dict, list, etc.)
- Boolean evaluation to False
- Customizable string representation
- Support for isinstance() checks with appropriate types

Example usage:
    >>> from superconf.lib.sentinel import NOT_SET
    >>> value = NOT_SET
    >>> if value is NOT_SET:
    ...     print("Value not set")
    Value not set
    
    >>> # Boolean evaluation
    >>> bool(NOT_SET)
    False
    
    >>> # String representation
    >>> str(NOT_SET)
    '<NOT_SET>'
"""

from sentinel import create


class Sentinel:
    "Main sentinal class"

    _instance = None
    __name__ = None

    def __bool__(self):
        return False

    def __str__(self):
        return f"<{self.__name__}>"

    def __repr__(self):
        return f"<|{self.__name__}|>"

    @property
    def type(self):
        "Return the type of the sentinel"
        return self.__class__


cls_dict = {
    "__str__": lambda self: f"<{repr(self)}>",
    "type": property(lambda self: Sentinel),
}
container_cls_dict = {
    "type": property(lambda self: Sentinel),
}


NOT_SET = create(name="NOT_SET", mro=Sentinel.__mro__, cls_dict=cls_dict)


class SentinelObj(Sentinel):
    """
    A sentinel object that behaves like an empty dict but is identifiable as NOT_SET_OBJ.
    Passes the isinstance(NOT_SET_OBJ, dict) test.
    All methods are read-only.
    """

    def __getattr__(self, *_):
        return NOT_SET


# Dictionary sentinel
class SentinelDict(dict, SentinelObj):
    """
    A sentinel dictionary that behaves like an empty dict but is identifiable as NOT_SET_DICT.
    Passes the isinstance(NOT_SET_DICT, dict) test.
    All methods are read-only.
    """

    def __bool__(self):
        return False

    # Override mutating methods to make this dict read-only
    def __setitem__(self, key, value):
        raise TypeError("NOT_SET_DICT is immutable")

    def clear(self):
        raise TypeError("NOT_SET_DICT is immutable")

    def pop(self, *args, **kwargs):
        raise TypeError("NOT_SET_DICT is immutable")

    def popitem(self):
        raise KeyError("NOT_SET_DICT is immutable")

    def update(self, *args, **kwargs):
        raise TypeError("NOT_SET_DICT is immutable")

    def setdefault(self, *args, **kwargs):
        raise TypeError("NOT_SET_DICT is immutable")

    def __delitem__(self, key):
        raise KeyError("NOT_SET_DICT is immutable")

    def __ior__(self, other):
        raise TypeError("NOT_SET_DICT is immutable")

    # Full compatibility with dict
    def __repr__(self):
        return "{}"

    def __str__(self):
        return "{}"


# List sentinel
class SentinelList(list, SentinelObj):
    """
    A sentinel list that behaves like an empty list but is identifiable as NOT_SET_LIST.
    Passes the isinstance(NOT_SET_LIST, list) test.
    All methods are read-only.
    """

    def __bool__(self):
        return False

    # Override mutating methods to make this list read-only
    def __setitem__(self, key, value):
        raise TypeError("NOT_SET_LIST is immutable")

    def append(self, item):
        raise TypeError("NOT_SET_LIST is immutable")

    def extend(self, iterable):
        raise TypeError("NOT_SET_LIST is immutable")

    def insert(self, index, item):
        raise TypeError("NOT_SET_LIST is immutable")

    def remove(self, item):
        raise TypeError("NOT_SET_LIST is immutable")

    def pop(self, *args, **kwargs):
        raise TypeError("NOT_SET_LIST is immutable")

    def clear(self):
        raise TypeError("NOT_SET_LIST is immutable")

    def sort(self, *args, **kwargs):
        raise TypeError("NOT_SET_LIST is immutable")

    def reverse(self):
        raise TypeError("NOT_SET_LIST is immutable")


### INSTANCES


NOT_SET_DICT = create(
    "NOT_SET_DICT", mro=SentinelDict.__mro__, cls_dict=container_cls_dict
)
NOT_SET_LIST = create(
    "NOT_SET_LIST", mro=SentinelList.__mro__, cls_dict=container_cls_dict
)
NOT_SET_OBJ = create("NOT_SET_OBJ", mro=SentinelObj.__mro__, cls_dict=cls_dict)

UNSET_ARG = create("UNSET_ARG", mro=Sentinel.__mro__, cls_dict=cls_dict)
FAIL = create("FAIL", mro=Sentinel.__mro__, cls_dict=cls_dict)
DEFAULT = create("DEFAULT", mro=Sentinel.__mro__, cls_dict=cls_dict)


assert not isinstance(NOT_SET, type(None))
assert isinstance(NOT_SET_DICT, dict)
assert isinstance(NOT_SET_LIST, list)

assert len(NOT_SET_DICT) == 0
assert len(NOT_SET_LIST) == 0

assert not NOT_SET_DICT
assert not NOT_SET_LIST

assert isinstance(NOT_SET_LIST, NOT_SET_LIST.type)
assert isinstance(NOT_SET_DICT, type(NOT_SET_DICT))


def is_not_set(value):
    """Return True if value is a NOT_SET-family sentinel.

    Args:
        value: Any value to test.

    Returns:
        True when ``value`` is an instance of the NOT_SET sentinel type.
    """
    return isinstance(value, NOT_SET.type)
