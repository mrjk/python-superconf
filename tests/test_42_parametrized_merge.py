"""Parametrized and regression tests for merge strategies.

Documents intentional default behavior:

* dict / ConfigurationObj: ``override`` (deep merge) — same as before merge policies
* scalar fields: ``override`` — same as before
* list / FieldList / ConfigurationList: ``append`` — **changed** from old Leaf
  behavior which replaced the whole list when the right side was set
  (equivalent to today's ``replace``)
"""

import pytest

from superconf.configuration import (
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
)
from superconf.fields import Field, FieldInt, FieldList, FieldString
from superconf.merge import (
    MERGE_DICT_DEFAULT,
    MERGE_LIST_DEFAULT,
    MERGE_OTHER_DEFAULT,
    MergeKind,
    MergeStrategy,
    infer_merge_kind,
    merge_data,
    merge_maps,
    prefer_other_scalar,
)


# ---------------------------------------------------------------------------
# merge_data / helpers (unit)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "base, other, strategy, expected",
    [
        (["a"], ["b"], MergeStrategy.APPEND, ["a", "b"]),
        (["a"], ["b"], "append", ["a", "b"]),
        (["a"], ["b"], MergeStrategy.PREPEND, ["b", "a"]),
        (["a"], ["b"], MergeStrategy.REPLACE, ["b"]),
        (["a"], ["b"], MergeStrategy.KEEP, ["a"]),
        ([], ["b"], MergeStrategy.APPEND, ["b"]),
        (["a"], [], MergeStrategy.APPEND, ["a"]),
    ],
)
def test_merge_data_list_strategies(base, other, strategy, expected):
    """List merge_data strategies including string form."""
    assert merge_data(base, other, strategy, MergeKind.LIST) == expected


@pytest.mark.parametrize(
    "base, other, strategy, expected",
    [
        ({"a": 1}, {"b": 2}, MergeStrategy.OVERRIDE, {"a": 1, "b": 2}),
        ({"a": 1}, {"a": 9, "b": 2}, "override", {"a": 9, "b": 2}),
        ({"a": 1}, {"b": 2}, MergeStrategy.REPLACE, {"b": 2}),
        ({"a": 1}, {"b": 2}, MergeStrategy.KEEP, {"a": 1}),
        (
            {"a": 1, "b": 2},
            {"b": 9, "c": 3},
            MergeStrategy.OVERRIDE_PRESENT,
            {"a": 1, "b": 9},
        ),
        (
            {"a": 1, "b": 2},
            {"b": 9, "c": 3},
            MergeStrategy.OVERRIDE_ABSENT,
            {"a": 1, "b": 2, "c": 3},
        ),
        (
            {"nested": {"x": 1}},
            {"nested": {"y": 2}},
            MergeStrategy.OVERRIDE,
            {"nested": {"x": 1, "y": 2}},
        ),
    ],
)
def test_merge_data_dict_strategies(base, other, strategy, expected):
    """Dict merge_data strategies including nested override."""
    assert merge_data(base, other, strategy, MergeKind.DICT) == expected


@pytest.mark.parametrize(
    "base, other, strategy, expect_other",
    [
        ("left", "right", MergeStrategy.OVERRIDE, True),
        ("left", None, MergeStrategy.OVERRIDE_NON_NULL, False),
        ("left", "right", MergeStrategy.OVERRIDE_NON_NULL, True),
        ("left", "right", MergeStrategy.KEEP, False),
    ],
)
def test_prefer_other_scalar(base, other, strategy, expect_other):
    """Scalar prefer-other decision table."""
    assert prefer_other_scalar(base, other, strategy) is expect_other


def test_merge_data_rejects_override_on_list():
    """``override`` is not a valid list strategy."""
    with pytest.raises(ValueError, match="list merge strategy"):
        merge_data(["a"], ["b"], MergeStrategy.OVERRIDE, MergeKind.LIST)


def test_infer_merge_kind_from_values_and_strategy():
    """Kind inference from strategy and value types."""
    assert infer_merge_kind("append") == MergeKind.LIST
    assert infer_merge_kind("override_present") == MergeKind.DICT
    assert infer_merge_kind("override_non_null") == MergeKind.OTHER
    assert infer_merge_kind("override", ["a"], ["b"]) == MergeKind.LIST
    assert infer_merge_kind("override", {"a": 1}, {"b": 2}) == MergeKind.DICT
    assert infer_merge_kind("override", "a", "b") == MergeKind.OTHER


def test_merge_maps_with_merge_both_callback():
    """merge_maps delegates conflicts to merge_both."""
    result = merge_maps(
        {"a": 1, "b": 2},
        {"b": 20, "c": 3},
        MergeStrategy.OVERRIDE,
        merge_both=lambda left, right: left + right,
    )
    assert result == {"a": 1, "b": 22, "c": 3}


# ---------------------------------------------------------------------------
# Default policies (regression: intentional list default change)
# ---------------------------------------------------------------------------


def test_type_defaults_are_documented():
    """Lock type defaults: list=append, dict/other=override."""
    assert MERGE_LIST_DEFAULT == MergeStrategy.APPEND
    assert MERGE_DICT_DEFAULT == MergeStrategy.OVERRIDE
    assert MERGE_OTHER_DEFAULT == MergeStrategy.OVERRIDE


def test_field_list_default_policy_is_append():
    """FieldList nodes resolve merge=append by default."""

    class AppConfig(ConfigurationObj):
        tags = FieldList(default=["x"])
        name = FieldString(default="n")

    config = AppConfig(value={"tags": ["a"], "name": "left"})
    assert config.__node_merge__ == MergeStrategy.OVERRIDE
    assert config.__node_children__["tags"].__node_merge__ == MergeStrategy.APPEND
    assert config.__node_children__["name"].__node_merge__ == MergeStrategy.OVERRIDE


def test_field_list_merge_appends_by_default():
    """Merging FieldList children concatenates (new default, not replace)."""

    class AppConfig(ConfigurationObj):
        tags = FieldList(default=[])
        name = FieldString(default="n")

    left = AppConfig(value={"tags": ["a", "b"], "name": "L"})
    right = AppConfig(value={"tags": ["c"], "name": "R"})
    merged = left.merge(right)

    assert merged.get_value() == {"tags": ["a", "b", "c"], "name": "R"}


def test_field_list_old_behavior_via_replace():
    """Old Leaf list behavior is available with merge=replace."""

    class AppConfig(ConfigurationObj):
        tags = FieldList(default=[], merge=MergeStrategy.REPLACE)
        name = FieldString(default="n")

    left = AppConfig(value={"tags": ["a", "b"], "name": "L"})
    right = AppConfig(value={"tags": ["c"], "name": "R"})
    merged = left.merge(right)

    assert merged.get_value() == {"tags": ["c"], "name": "R"}


def test_configuration_list_default_appends():
    """ConfigurationList default merge is append."""

    class Items(ConfigurationList):
        pass

    left = Items(value=["a", "b"])
    right = Items(value=["c"])
    assert left.__node_merge__ == MergeStrategy.APPEND
    assert left.merge(right).get_value() == ["a", "b", "c"]


# ---------------------------------------------------------------------------
# ConfigurationObj / Dict merge
# ---------------------------------------------------------------------------


def test_configuration_obj_default_deep_override():
    """ConfigurationObj deep-merges with right-wins scalars (unchanged)."""

    class AppConfig(ConfigurationObj):
        name = FieldString(default="default")
        count = FieldInt(default=999)

    left = AppConfig(value={"name": "toto", "count": 25})
    right = AppConfig(value={"name": "titi"})
    merged = left.merge(right)

    assert merged.get_value() == {"name": "titi", "count": 25}


@pytest.mark.parametrize(
    "strategy, left_val, right_val, expected",
    [
        (
            MergeStrategy.REPLACE,
            {"name": "a", "count": 1},
            {"name": "b"},
            {"name": "b", "count": 999},
        ),
        (
            MergeStrategy.KEEP,
            {"name": "a", "count": 1},
            {"name": "b"},
            {"name": "a", "count": 1},
        ),
        (
            MergeStrategy.OVERRIDE_PRESENT,
            {"name": "a", "count": 1},
            {"name": "b", "extra": 9},
            {"name": "b", "count": 1},
        ),
        (
            MergeStrategy.OVERRIDE_ABSENT,
            {"name": "a", "count": 1},
            {"name": "b", "extra": 9},
            {"name": "a", "count": 1, "extra": 9},
        ),
    ],
)
def test_configuration_obj_meta_merge_strategies(
    strategy, left_val, right_val, expected
):
    """Meta.merge strategies on ConfigurationObj."""

    class AppConfig(ConfigurationObj):
        class Meta:
            merge = strategy
            extra_fields = True

        name = FieldString(default="default")
        count = FieldInt(default=999)

    left = AppConfig(value=left_val)
    right = AppConfig(value=right_val)
    assert left.merge(right).get_value() == expected


def test_field_merge_overrides_meta():
    """Field merge kwarg beats class Meta.merge for that child."""

    class AppConfig(ConfigurationObj):
        class Meta:
            merge = MergeStrategy.OVERRIDE

        locked = FieldInt(default=1, merge=MergeStrategy.KEEP)
        name = FieldString(default="x")

    left = AppConfig(value={"locked": 10, "name": "left"})
    right = AppConfig(value={"locked": 99, "name": "right"})
    merged = left.merge(right)

    assert merged.get_value() == {"locked": 10, "name": "right"}


def test_scalar_override_non_null_keeps_when_other_is_none():
    """override_non_null does not take None from the right side."""

    class AppConfig(ConfigurationObj):
        name = Field(default="x", merge=MergeStrategy.OVERRIDE_NON_NULL)

    left = AppConfig(value={"name": "left"})
    right = AppConfig(value={"name": None})
    assert left.merge(right).get_value()["name"] == "left"


def test_configuration_dict_nested_override():
    """ConfigurationDict deep-merges nested ConfigurationObj children."""

    class AppConfig(ConfigurationObj):
        name = FieldString(default="default")
        count = FieldInt(default=999)

    class AppDict(ConfigurationDict):
        class Meta:
            children_class = AppConfig

    left = AppDict(
        value={
            "app1": {"name": "toto", "count": 64},
            "app2": {"name": "titi"},
        }
    )
    right = AppDict(
        value={
            "app1": {"name": "tata"},
            "app3": {"name": "tutu"},
        }
    )
    merged = left.merge(right)

    assert merged.get_value() == {
        "app1": {"name": "tata", "count": 64},
        "app2": {"name": "titi", "count": 999},
        "app3": {"name": "tutu", "count": 999},
    }


@pytest.mark.parametrize(
    "strategy, expected",
    [
        (MergeStrategy.APPEND, ["a", "b", "c"]),
        (MergeStrategy.PREPEND, ["c", "a", "b"]),
        (MergeStrategy.REPLACE, ["c"]),
        (MergeStrategy.KEEP, ["a", "b"]),
        ("append", ["a", "b", "c"]),
        ("replace", ["c"]),
    ],
)
def test_configuration_list_meta_strategies(strategy, expected):
    """ConfigurationList Meta.merge strategies (enum and string)."""

    class Items(ConfigurationList):
        class Meta:
            merge = strategy

    left = Items(value=["a", "b"])
    right = Items(value=["c"])
    assert left.merge(right).get_value() == expected


def test_enum_and_string_merge_meta_are_equivalent():
    """MergeStrategy enum and plain string Meta.merge behave the same."""

    class CfgEnum(ConfigurationObj):
        class Meta:
            merge = MergeStrategy.REPLACE

        name = FieldString(default="left")

    class CfgStr(ConfigurationObj):
        class Meta:
            merge = "replace"

        name = FieldString(default="left")

    left_enum = CfgEnum(value={"name": "a"})
    right_enum = CfgEnum(value={"name": "b"})
    left_str = CfgStr(value={"name": "a"})
    right_str = CfgStr(value={"name": "b"})

    assert left_enum.__node_merge__ is MergeStrategy.REPLACE
    assert left_str.__node_merge__ is MergeStrategy.REPLACE
    assert left_enum.merge(right_enum).get_value() == left_str.merge(
        right_str
    ).get_value()
