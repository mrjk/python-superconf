# pylint: skip-file


import pytest

from superconf.casts import (
    AsBoolean,
    AsDict,
    AsIdentity,
    AsInt,
    AsList,
    AsOption,
    AsTuple,
    InvalidCastConfiguration,
)

# from superconf.common import NOT_SET


class TestAsBoolean:
    def test_true_values(self):
        cast = AsBoolean()
        true_values = ["1", "true", "True", "YES", "y", "ON", "t"]
        for value in true_values:
            assert cast(value) is True

    def test_false_values(self):
        cast = AsBoolean()
        false_values = ["0", "false", "False", "NO", "n", "OFF", "f"]
        for value in false_values:
            assert cast(value) is False

    def test_custom_values(self):
        cast = AsBoolean({"si": True, "nope": False})
        assert cast("si") is True
        assert cast("nope") is False

    def test_invalid_value(self):
        cast = AsBoolean()
        with pytest.raises(InvalidCastConfiguration):
            cast("invalid")


class TestAsInt:
    def test_valid_integers(self):
        cast = AsInt()
        assert cast("10") == 10
        assert cast("-5") == -5
        assert cast("0") == 0

    def test_invalid_integer(self):
        cast = AsInt()
        with pytest.raises(InvalidCastConfiguration):
            cast("invalid")
        with pytest.raises(InvalidCastConfiguration):
            cast("10.5")


class TestAsList:
    def test_empty_input(self):
        cast = AsList()
        assert cast("") == []
        assert cast([]) == []

    def test_string_input(self):
        cast = AsList()
        assert cast("a,b,c") == ["a", "b", "c"]
        assert cast("item1, item2, item3") == ["item1", "item2", "item3"]

    def test_quoted_strings(self):
        cast = AsList()
        assert cast('"a,b",c') == ['"a,b"', "c"]
        assert cast("'x,y',z") == ["'x,y'", "z"]

    def test_sequence_input(self):
        cast = AsList()
        assert cast(["a", "b", "c"]) == ["a", "b", "c"]
        assert cast(("x", "y", "z")) == ["x", "y", "z"]

    def test_custom_delimiter(self):
        cast = AsList(delimiter=";")
        assert cast("a;b;c") == ["a", "b", "c"]

    def test_invalid_input(self):
        cast = AsList()
        with pytest.raises(AssertionError):
            cast({"key": "value"})


class TestAsTuple:
    def test_empty_input(self):
        cast = AsTuple()
        assert cast("") == ()
        assert cast([]) == ()

    def test_string_input(self):
        cast = AsTuple()
        assert cast("a,b,c") == ("a", "b", "c")
        assert cast("item1, item2, item3") == ("item1", "item2", "item3")

    def test_sequence_input(self):
        cast = AsTuple()
        assert cast(["a", "b", "c"]) == ("a", "b", "c")
        assert cast(("x", "y", "z")) == ("x", "y", "z")


class TestAsDict:
    def test_empty_input(self):
        cast = AsDict()
        assert cast("") == {}
        assert cast({}) == {}

    def test_dict_input(self):
        cast = AsDict()
        input_dict = {"key": "value", "another": "pair"}
        assert cast(input_dict) == input_dict

    def test_invalid_input(self):
        cast = AsDict()
        with pytest.raises(AssertionError):
            cast("key=value,other=pair")
        with pytest.raises(AssertionError):
            cast(["key", "value"])


class TestAsOption:
    def test_valid_option(self):
        options = {"dev": [1, 2, 3], "prod": [4, 5, 6]}
        cast = AsOption(options)
        assert cast("dev") == [1, 2, 3]
        assert cast("prod") == [4, 5, 6]

    def test_invalid_option_no_default(self):
        cast = AsOption({"dev": 1, "prod": 2})
        with pytest.raises(InvalidCastConfiguration):
            cast("invalid")

    def test_invalid_option_with_default(self):
        options = {"dev": 1, "prod": 2}
        cast = AsOption(options, default_option="dev")
        assert cast("invalid") == 1

    def test_invalid_default_option(self):
        options = {"dev": 1, "prod": 2}
        cast = AsOption(options, default_option="invalid")
        with pytest.raises(InvalidCastConfiguration):
            cast("something")


class TestAsIdentity:
    def test_identity_cast(self):
        cast = AsIdentity()
        assert cast("test") == "test"
        assert cast(123) == 123
        assert cast([1, 2, 3]) == [1, 2, 3]
        assert cast(None) is None
