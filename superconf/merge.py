"""Merge strategies and generic merge helpers for configuration values."""

from enum import Enum
from typing import Any, Callable, Dict, Iterable, Mapping, Optional

from superconf.lib.sentinel_v2 import is_not_set

_MISSING = object()


def _unique(seq: Iterable[Any]) -> list:
    """Remove duplicates from a sequence while preserving order.

    Local copy avoids importing ``superconf.common`` (which re-exports this
    module and would create a cyclic import).
    """
    seen: set = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


class MergeKind(str, Enum):
    """Value shape that selects which merge strategies are valid."""

    OTHER = "other"
    DICT = "dict"
    LIST = "list"


class MergeStrategy(str, Enum):
    """Merge policy values usable as enum members or plain strings.

    Examples:
        merge = MergeStrategy.OVERRIDE
        merge = "override"  # equivalent
    """

    OVERRIDE = "override"
    OVERRIDE_NON_NULL = "override_non_null"
    OVERRIDE_PRESENT = "override_present"
    OVERRIDE_ABSENT = "override_absent"
    REPLACE = "replace"
    KEEP = "keep"
    APPEND = "append"
    PREPEND = "prepend"


# Backward-compatible aliases (enum members; also compare equal to strings)
MERGE_OVERRIDE = MergeStrategy.OVERRIDE
MERGE_OVERRIDE_NON_NULL = MergeStrategy.OVERRIDE_NON_NULL
MERGE_OVERRIDE_PRESENT = MergeStrategy.OVERRIDE_PRESENT
MERGE_OVERRIDE_ABSENT = MergeStrategy.OVERRIDE_ABSENT
MERGE_REPLACE = MergeStrategy.REPLACE
MERGE_KEEP = MergeStrategy.KEEP
MERGE_APPEND = MergeStrategy.APPEND
MERGE_PREPEND = MergeStrategy.PREPEND

_KIND_ALLOWED = {
    MergeKind.OTHER: frozenset(
        (
            MergeStrategy.OVERRIDE,
            MergeStrategy.OVERRIDE_NON_NULL,
            MergeStrategy.KEEP,
        )
    ),
    MergeKind.DICT: frozenset(
        (
            MergeStrategy.OVERRIDE,
            MergeStrategy.REPLACE,
            MergeStrategy.OVERRIDE_PRESENT,
            MergeStrategy.OVERRIDE_ABSENT,
            MergeStrategy.KEEP,
        )
    ),
    MergeKind.LIST: frozenset(
        (
            MergeStrategy.REPLACE,
            MergeStrategy.PREPEND,
            MergeStrategy.APPEND,
            MergeStrategy.KEEP,
        )
    ),
}

_KIND_DEFAULT = {
    MergeKind.OTHER: MergeStrategy.OVERRIDE,
    MergeKind.DICT: MergeStrategy.OVERRIDE,
    MergeKind.LIST: MergeStrategy.APPEND,
}

MERGE_OTHER_STRATEGIES = tuple(_KIND_ALLOWED[MergeKind.OTHER])
MERGE_DICT_STRATEGIES = tuple(_KIND_ALLOWED[MergeKind.DICT])
MERGE_LIST_STRATEGIES = tuple(_KIND_ALLOWED[MergeKind.LIST])

MERGE_OTHER_DEFAULT = _KIND_DEFAULT[MergeKind.OTHER]
MERGE_DICT_DEFAULT = _KIND_DEFAULT[MergeKind.DICT]
MERGE_LIST_DEFAULT = _KIND_DEFAULT[MergeKind.LIST]


def normalize_merge_strategy(value: Any) -> MergeStrategy:
    """Normalize a merge strategy from enum or string to ``MergeStrategy``.

    Args:
        value: A ``MergeStrategy`` member or its string value.

    Returns:
        The matching ``MergeStrategy`` member.

    Raises:
        ValueError: If value is not a known merge strategy.
    """
    if isinstance(value, MergeStrategy):
        return value
    if isinstance(value, str):
        try:
            return MergeStrategy(value)
        except ValueError as exc:
            allowed = ", ".join(repr(s.value) for s in MergeStrategy)
            raise ValueError(
                f"Invalid merge strategy {value!r}, expected one of: {allowed}"
            ) from exc
    raise ValueError(
        f"Invalid merge strategy type {type(value).__name__}: {value!r}, "
        f"expected MergeStrategy or str"
    )


def ensure_merge_strategy(strategy: Any, kind: MergeKind) -> MergeStrategy:
    """Normalize strategy and ensure it is allowed for ``kind``.

    Args:
        strategy: Enum member or string strategy.
        kind: Merge value kind.

    Returns:
        Normalized ``MergeStrategy``.

    Raises:
        ValueError: If strategy is unknown or invalid for kind.
    """
    strategy = normalize_merge_strategy(strategy)
    allowed = _KIND_ALLOWED[kind]
    if strategy not in allowed:
        raise ValueError(
            f"Invalid {kind.value} merge strategy '{strategy}', "
            f"expected one of: {tuple(allowed)}"
        )
    return strategy


def is_merge_value_set(value: Any) -> bool:
    """Return True when value is a concrete merge source (not NOT_SET)."""
    return not is_not_set(value)


def infer_merge_kind(
    strategy: Any,
    base: Any = None,
    other: Any = None,
) -> MergeKind:
    """Infer merge kind from strategy and optional sample values.

    Args:
        strategy: Enum member or string strategy.
        base: Optional left-hand value used for type inference.
        other: Optional right-hand value used for type inference.

    Returns:
        Inferred ``MergeKind``.
    """
    strategy = normalize_merge_strategy(strategy)
    if strategy in (MergeStrategy.PREPEND, MergeStrategy.APPEND):
        return MergeKind.LIST
    if strategy in (MergeStrategy.OVERRIDE_PRESENT, MergeStrategy.OVERRIDE_ABSENT):
        return MergeKind.DICT
    if strategy == MergeStrategy.OVERRIDE_NON_NULL:
        return MergeKind.OTHER
    if isinstance(base, list) or isinstance(other, list):
        return MergeKind.LIST
    if isinstance(base, dict) or isinstance(other, dict):
        return MergeKind.DICT
    return MergeKind.OTHER


def prefer_other_scalar(
    base: Any,
    other: Any,
    strategy: Any,
    *,
    is_set: Callable[[Any], bool] = is_merge_value_set,
) -> bool:
    """Return True when scalar merge should take ``other`` over ``base``.

    Args:
        base: Left-hand scalar value.
        other: Right-hand scalar value.
        strategy: Scalar merge strategy.
        is_set: Predicate for whether a value is present.

    Returns:
        True if ``other`` wins.
    """
    strategy = ensure_merge_strategy(strategy, MergeKind.OTHER)
    other_set = is_set(other)
    if strategy == MergeStrategy.OVERRIDE:
        return other_set
    if strategy == MergeStrategy.OVERRIDE_NON_NULL:
        return other_set and other is not None
    # KEEP
    return (not is_set(base)) and other_set


def merge_data(
    base: Any,
    other: Any,
    strategy: Any,
    kind: Optional[MergeKind] = None,
) -> Any:
    """Merge two plain values (list/dict) according to strategy.

    Args:
        base: Left-hand value.
        other: Right-hand value.
        strategy: Merge strategy (enum or string).
        kind: Explicit kind; inferred when omitted.

    Returns:
        Merged value (new list/dict).

    Raises:
        ValueError: If strategy/kind combination is invalid.
    """
    if kind is None:
        kind = infer_merge_kind(strategy, base, other)
    strategy = ensure_merge_strategy(strategy, kind)

    if kind == MergeKind.LIST:
        base_list = list(base) if base is not None else []
        other_list = list(other) if other is not None else []
        if strategy == MergeStrategy.REPLACE:
            return other_list
        if strategy == MergeStrategy.KEEP:
            return base_list
        if strategy == MergeStrategy.APPEND:
            return base_list + other_list
        # PREPEND
        return other_list + base_list

    if kind == MergeKind.DICT:
        base_dict = dict(base) if base is not None else {}
        other_dict = dict(other) if other is not None else {}
        if strategy == MergeStrategy.REPLACE:
            merged = dict(other_dict)
        elif strategy == MergeStrategy.KEEP:
            merged = dict(base_dict)
        else:
            merged = merge_maps(
                base_dict,
                other_dict,
                strategy,
                merge_both=_deep_merge_dict_values,
            )
        return merged

    raise ValueError(f"merge_data does not support kind {kind!r}")


def _deep_merge_dict_values(base: Any, other: Any) -> Any:
    """Recursively merge nested dict values; otherwise prefer ``other``."""
    if isinstance(base, dict) and isinstance(other, dict):
        return merge_data(base, other, MergeStrategy.OVERRIDE, MergeKind.DICT)
    return other


def merge_maps(
    base: Mapping,
    other: Mapping,
    strategy: Any,
    *,
    merge_both: Callable[[Any, Any], Any],
    missing: Any = _MISSING,
) -> Dict:
    """Merge two key/value maps with a dict merge strategy.

    Args:
        base: Left-hand mapping.
        other: Right-hand mapping.
        strategy: Dict merge strategy.
        merge_both: Called when both sides have a key and strategy merges them.
        missing: Sentinel for absent keys.

    Returns:
        New dict with merged entries.
    """
    strategy = ensure_merge_strategy(strategy, MergeKind.DICT)

    if strategy == MergeStrategy.REPLACE:
        return dict(other)
    if strategy == MergeStrategy.KEEP:
        return dict(base)

    out: Dict = {}
    if strategy == MergeStrategy.OVERRIDE_ABSENT:
        out = dict(base)
        for key, right in other.items():
            if key not in out:
                out[key] = right
        return out

    if strategy == MergeStrategy.OVERRIDE_PRESENT:
        keys: Iterable = base.keys()
    else:
        keys = _unique(list(base.keys()) + list(other.keys()))

    for key in keys:
        left = base[key] if key in base else missing
        right = other[key] if key in other else missing
        if left is not missing and right is not missing:
            out[key] = merge_both(left, right)
        elif left is not missing:
            out[key] = left
        elif right is not missing:
            out[key] = right
    return out


# Thin aliases kept for existing callers / docs
def merge_list_data(base, other, strategy):
    """Merge two list values according to a list merge strategy."""
    return merge_data(base, other, strategy, MergeKind.LIST)


def merge_dict_data(base, other, strategy):
    """Merge two dict values according to a dict merge strategy."""
    return merge_data(base, other, strategy, MergeKind.DICT)
