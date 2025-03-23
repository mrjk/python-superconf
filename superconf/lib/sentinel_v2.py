import sentinel


class Sentinel:
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


# Dictionary sentinel
class SentinelDict(dict, Sentinel):
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
class SentinelList(list, Sentinel):
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


cls_dict = {
    "__str__": lambda self: f"<{repr(self)}>",
    "type": property(lambda self: Sentinel),
}


NOT_SET = sentinel.create(name="NOT_SET", mro=Sentinel.__mro__, cls_dict=cls_dict)
NOT_SET_DICT = sentinel.create(
    "NOT_SET_DICT", mro=SentinelDict.__mro__, cls_dict=cls_dict
)
NOT_SET_LIST = sentinel.create(
    "NOT_SET_LIST", mro=SentinelList.__mro__, cls_dict=cls_dict
)

UNSET_ARG = sentinel.create("UNSET_ARG", mro=Sentinel.__mro__, cls_dict=cls_dict)
FAIL = sentinel.create("FAIL", mro=Sentinel.__mro__, cls_dict=cls_dict)
DEFAULT = sentinel.create("DEFAULT", mro=Sentinel.__mro__, cls_dict=cls_dict)


assert NOT_SET is NOT_SET
assert not isinstance(NOT_SET, type(None))
assert isinstance(NOT_SET_DICT, dict)
assert isinstance(NOT_SET_LIST, list)

assert len(NOT_SET_DICT) == 0
assert len(NOT_SET_LIST) == 0

assert not NOT_SET_DICT
assert not NOT_SET_LIST

assert type(NOT_SET_LIST) == type(NOT_SET_LIST)
assert type(NOT_SET_DICT) == type(NOT_SET_DICT)
