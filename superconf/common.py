"""
Common part of code and helpers
"""

import json

# Class helpers
# --------------------


def obj_repr(self):
    "Default python representation of an object"
    addr = hex(id(self))
    name = f"{self.__class__.__module__}.{self.__class__.__name__}"
    out = f"<{name} object at {addr}>"
    return out


def obj_repr_short(self):
    "Shorter python representation of an object"
    addr = hex(id(self))
    name = f"{self.__class__.__module__}.{self.__class__.__name__}"
    out = f"<{name}({addr})>"
    return out


# Functions helpers
# --------------------


def list_to_dict(array, key=None):
    "Transform a list to a dict in number as string for keys"
    return {str(v.__dict__.get(key, k) if key else k): v for k, v in enumerate(array)}


def dict_to_list(map):
    "Transform a dict to a list. Original dick keys are lost"
    return list(map.values())


def to_json(obj, fn=None, indent=2, default=None, **kwargs):
    "Return a node object to serializable thing"
    fn = fn if fn else default

    def t_funct(item):
        return str(item)

        # if item is UNSET:
        #     return None
        # if hasattr(item, "get_value"):
        #     return item.get_value()
        # raise Exception(f"Unparseable item: {item}")

    return json.dumps(obj, indent=indent, default=fn or t_funct, **kwargs)


dict_to_json = to_json

# Objectss helpers
# --------------------


class NotSet(str):
    """
    A special type that behaves as a replacement for None.
    We have to put a new default value to know if a variable has been set by
    the user explicitly. This is useful for the ``CommandLine`` loader, when
    CLI parsers force you to set a default value, and thus, break the discovery
    chain.
    """

    pass

    def __str__(self):
        return "<NOT_SET>"

    def __repr__(self):
        addr = hex(id(self))
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        out = f"<{name} object at {addr}>"
        return out


class UnSet(object):
    """
    A special type that behaves as a replacement for None.
    """

    def __str__(self):
        return "<UNSET>"

    def __repr__(self):
        addr = hex(id(self))
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        out = f"<{name} object at {addr}>"
        return out

    def __getitem__(self, key):
        return self

    def __get__(self, *args):
        return self

    def __getattr__(self, key):
        return self

    def __call__(self, *args, **kwargs):
        return self

    def __len__(self):
        return self

    def __dict__(self):
        return {}

    def __index__(self):
        return 0

    def __bool__(self):
        return False

    def __iter__(self):
        yield from dict().items()

    def __contains__(self, value):
        return False

    def __int__(self):
        return 0


NOT_SET = NotSet()
UNSET = UnSet()


def filter_NOT_UNSET(array, only=None, key=None):
    assert isinstance(array, list)
    out = []
    for item in array:
        if item == NOT_SET:
            continue
        if item == UNSET:
            continue
        if only is not None:
            if not isinstance(item, only):
                continue
        if key is not None:
            if not isinstance(item, dict):
                continue
            if not key in item:
                continue

        out.append(item)
    return out
