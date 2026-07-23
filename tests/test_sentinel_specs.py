# pylint: skip-file

import pytest

from superconf.lib.sentinel import (  # DEFAULT,; FAIL,; NOT_SET,; NOT_SET_LIST,; UNSET_ARG,
    NOT_SET_DICT,
)


def assert_true(value):
    "Wrapper for assert value"
    assert value


def assert_false(value):
    "Wrapper for assert not value"
    assert not value


def assert_type_error(value):
    with pytest.raises(TypeError):
        assert value


def assert_key_error(value):
    with pytest.raises(KeyError):
        assert value


PARAM_RO = [
    [lambda: {}, assert_true],
    [lambda: NOT_SET_DICT, assert_true],
]


# =========== Read-only methods tests ===========


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_contains(obj, assert_fn):
    empty_dict = obj()
    assert_fn("anything" not in empty_dict)


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_eq(obj, assert_fn):
    empty_dict = obj()
    assert_fn(empty_dict == {})
    assert_fn(empty_dict != {"a": 1})
    assert_fn(empty_dict != {"x": None})


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_getitem(obj, assert_fn):
    empty_dict = obj()

    ret = False
    try:
        _ = empty_dict["anything"]
    except KeyError:
        ret = True

    assert_fn(ret)


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_iter(obj, assert_fn):
    empty_dict = obj()
    keys = []
    for key in empty_dict:
        keys.append(key)
    assert_fn(keys == [])


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_len(obj, assert_fn):
    empty_dict = obj()
    assert_fn(len(empty_dict) == 0)


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_repr_str(obj, assert_fn):
    empty_dict = obj()
    # Both __repr__ and __str__ should produce valid representations
    assert_fn(eval(repr(empty_dict)) == empty_dict)
    assert_fn(isinstance(str(empty_dict), str))
    assert_fn(str(empty_dict) == "{}")


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_reversed(obj, assert_fn):
    empty_dict = obj()
    # Test that reversed works on empty dict
    rev_keys = list(reversed(empty_dict))
    assert_fn(rev_keys == [])


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_copy(obj, assert_fn):
    empty_dict = obj()
    copied = empty_dict.copy()
    assert_fn(copied == empty_dict)
    assert_fn(id(copied) != id(empty_dict))  # Different objects


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_get(obj, assert_fn):
    empty_dict = obj()
    assert_fn(empty_dict.get("anything") is None)
    assert_fn(empty_dict.get("anything", "default") == "default")


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_items(obj, assert_fn):
    empty_dict = obj()
    items = empty_dict.items()
    assert_fn(list(items) == [])


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_keys(obj, assert_fn):
    empty_dict = obj()
    keys = empty_dict.keys()
    assert_fn(list(keys) == [])


@pytest.mark.parametrize("obj,assert_fn", PARAM_RO)
def test_ro_values(obj, assert_fn):
    empty_dict = obj()
    values = empty_dict.values()
    assert_fn(list(values) == [])


# No parametrization of fromkeys test since it doesn't use the factory
def test_ro_fromkeys():
    # Empty list of keys
    d1 = dict.fromkeys([])
    assert d1 == {}

    # Empty dict with non-empty keys
    d2 = dict.fromkeys(["a", "b", "c"])
    assert len(d2) == 3
    assert all(v is None for v in d2.values())

    # Empty dict with custom value
    d3 = dict.fromkeys([], 42)
    assert d3 == {}


# =========== Mutation methods tests ===========

PARAM_RW = [
    [lambda: {}, True],
    [lambda: NOT_SET_DICT, TypeError],
]

PARAM_RW_KEY_ERROR = [
    [lambda: {}, KeyError],
    [lambda: NOT_SET_DICT, KeyError],
]


@pytest.mark.parametrize("obj,result", PARAM_RW_KEY_ERROR)
def test_rw_delitem(obj, result):

    empty_dict = obj()
    ret = None
    try:
        del empty_dict["nonexistent"]
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_or_operations(obj, result):
    empty_dict = obj()
    other_dict = {"a": 1, "b": 2}

    # __or__ (|) should work for both as it creates a new dict
    result2 = empty_dict | other_dict
    assert result2 == {"a": 1, "b": 2}
    assert empty_dict == {}

    ret = None
    try:
        empty_dict |= other_dict
        assert empty_dict == {"a": 1, "b": 2}
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should get {result}, got {ret}"


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_setitem(obj, result):
    empty_dict = obj()

    ret = None
    try:
        empty_dict["key"] = "value"
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"

    if result == True:
        assert empty_dict["key"] == "value"
        assert len(empty_dict) == 1
    else:
        assert empty_dict == {}
        assert len(empty_dict) == 0


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_clear(obj, result):
    empty_dict = obj()

    # Only try to add something for mutable dicts
    if result == True:
        empty_dict["key"] = "value"

    ret = None
    try:
        empty_dict.clear()
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"

    assert len(empty_dict) == 0
    assert empty_dict == {}


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_pop(obj, result):
    empty_dict = obj()

    ret = None
    try:
        empty_dict.pop("nonexistent", "default")
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"

    if result == True:
        # Pop with default from empty dict
        value = empty_dict.pop("nonexistent", "default")
        assert value == "default"

        # Pop non-existent without default
        ret = False
        try:
            empty_dict.pop("nonexistent")
        except KeyError:
            ret = True

        assert ret


@pytest.mark.parametrize("obj,result", PARAM_RW_KEY_ERROR)
def test_rw_popitem(obj, result):
    empty_dict = obj()

    ret = None
    try:
        empty_dict.popitem()
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_setdefault(obj, result):
    empty_dict = obj()

    ret = None
    try:
        empty_dict.setdefault("key", "value")
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"

    if result == True:
        # Non-existing key sets new value
        value = empty_dict.setdefault("key", "value")
        assert value == "value"
        assert empty_dict["key"] == "value"

        # Using setdefault with no default value
        empty_dict.clear()
        value = empty_dict.setdefault("key")
        assert value is None
        assert empty_dict["key"] is None


@pytest.mark.parametrize("obj,result", PARAM_RW)
def test_rw_update(obj, result):
    empty_dict = obj()

    ret = None
    try:
        empty_dict.update({"a": 1, "b": 2})
        ret = True
    except Exception as err:
        ret = type(err)

    assert ret == result, f"{type(empty_dict)} should raise {result}, got {ret}"

    if result == True:
        # Update worked, verify the result
        assert empty_dict == {"a": 1, "b": 2}

        # Clear and update with keyword args
        empty_dict.clear()
        empty_dict.update(c=3, d=4)
        assert empty_dict == {"c": 3, "d": 4}

        # Clear and update with sequence of pairs
        empty_dict.clear()
        empty_dict.update([("e", 5), ("f", 6)])
        assert empty_dict == {"e": 5, "f": 6}

        # Update with empty sources
        empty_dict.clear()
        empty_dict.update({})
        empty_dict.update()
        empty_dict.update([])
        assert empty_dict == {}
