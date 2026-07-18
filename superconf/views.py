"""Multi-source configuration views with configurable precedence.

A ``View`` decides which sources to consult and in what order. Each source is a
converter from ``superconf.sources`` that can ``load()`` a nested dict.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, List, Mapping, Optional, Sequence

from superconf.common import NOT_SET, UNSET_ARG
from superconf.sources.base import BaseSource, DataDict


# Highest priority first (12-factor friendly default names).
TWELVE_FACTOR_ORDER: List[str] = ["cli", "env", "file", "defaults"]


class ViewError(Exception):
    """Base error for view operations."""


class ViewOrderError(ViewError):
    """Raised when source order is invalid."""


class NoResults(ViewError):
    """Raised when a key is not found in any source."""


def _is_unset(value: Any) -> bool:
    """Return True if value is a NOT_SET sentinel."""
    return isinstance(value, NOT_SET.type)


def _deep_overlay(base: Any, overlay: Any) -> Any:
    """Merge overlay onto base; overlay wins on conflicts.

    Dicts are merged recursively. Lists and scalars from overlay replace base.
    NOT_SET in overlay is skipped (does not erase base). ``None`` is a real
    value and wins.

    Args:
        base: Existing value (lower priority).
        overlay: Incoming value (higher priority).

    Returns:
        Merged value.
    """
    if _is_unset(overlay):
        return deepcopy(base)

    if _is_unset(base):
        return deepcopy(overlay)

    if isinstance(base, Mapping) and isinstance(overlay, Mapping):
        result: DataDict = deepcopy(dict(base))
        for key, val in overlay.items():
            if _is_unset(val):
                continue
            if key in result:
                result[key] = _deep_overlay(result[key], val)
            else:
                result[key] = deepcopy(val)
        return result

    return deepcopy(overlay)


def _lookup_path(data: Mapping[str, Any], key: str) -> Any:
    """Return a top-level or dotted-path value from data.

    Args:
        data: Nested mapping.
        key: Top-level key, or dotted path (``db.host``).

    Returns:
        Found value, or ``UNSET_ARG`` if missing / unset.
    """
    if "." not in key:
        if key not in data:
            return UNSET_ARG
        value = data[key]
        return UNSET_ARG if _is_unset(value) else value

    current: Any = data
    for part in key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return UNSET_ARG
        current = current[part]
        if _is_unset(current):
            return UNSET_ARG
    return current


class View:
    """Ordered stack of sources for layered configuration lookup.

    Precedence is an explicit name list (highest priority first). Sources are
    converters; the view only loads them and resolves values.

    Args:
        order: Source names, highest priority first. Defaults to
            ``TWELVE_FACTOR_ORDER`` names when omitted (empty until sources
            are added — use ``set_order`` / pass explicit order).
    """

    def __init__(self, order: Optional[Sequence[str]] = None) -> None:
        self._sources: dict[str, BaseSource] = {}
        self._order: List[str] = list(order) if order is not None else []
        self._order_preset = order is not None

    def add(self, source: BaseSource) -> None:
        """Register a source by its ``name``.

        Args:
            source: Source converter instance.

        Raises:
            ViewOrderError: If a source with the same name already exists, or
                if a preset order was given and this name is not in it.
        """
        if source.name in self._sources:
            raise ViewOrderError(f"Source {source.name!r} already exists")
        if self._order_preset and source.name not in self._order:
            raise ViewOrderError(
                f"Source {source.name!r} is not in preset order {self._order}"
            )
        self._sources[source.name] = source
        if source.name not in self._order:
            self._order.append(source.name)

    def set_order(self, order: Sequence[str]) -> None:
        """Set precedence order (highest priority first).

        Unregistered names are allowed (skipped until ``add``). Duplicate
        names are rejected.

        Args:
            order: Source names, highest priority first.

        Raises:
            ViewOrderError: If order contains duplicates.
        """
        names = list(order)
        if len(names) != len(set(names)):
            raise ViewOrderError(f"Duplicate names in order: {names}")
        self._order = names
        self._order_preset = True

    def get_order(self) -> List[str]:
        """Return the current precedence list (highest first).

        Returns:
            Copy of the order list.
        """
        return list(self._order)

    def get_ordered_sources(self) -> List[BaseSource]:
        """Return registered sources in precedence order (highest first).

        Returns:
            Sources that appear in ``order`` and are registered. Names in
            order without a source are skipped.
        """
        return [
            self._sources[name]
            for name in self._order
            if name in self._sources
        ]

    def load_layers(self) -> List[tuple[str, DataDict]]:
        """Load all sources in precedence order.

        Returns:
            List of ``(name, data)`` pairs, highest priority first.
        """
        layers: List[tuple[str, DataDict]] = []
        for source in self.get_ordered_sources():
            layers.append((source.name, source.load()))
        return layers

    def materialize(self) -> DataDict:
        """Merge all layers into one nested dict.

        Applies sources from lowest to highest priority so higher layers win.
        Nested dicts merge deeply; lists/scalars replace.

        Returns:
            Resolved nested dictionary.
        """
        result: DataDict = {}
        for _name, data in reversed(self.load_layers()):
            result = _deep_overlay(result, data)
        return result if isinstance(result, dict) else {}

    def get(self, key: str, default: Any = UNSET_ARG) -> Any:
        """Return the first value found for ``key`` (highest priority wins).

        Args:
            key: Top-level key or dotted path.
            default: Value if missing; raises ``NoResults`` if still ``UNSET_ARG``.

        Returns:
            Resolved value.

        Raises:
            NoResults: If the key is absent from every source and no default.
        """
        report: List[str] = []
        value = self._query_first(key, report=report)
        if value is not UNSET_ARG:
            return value
        if default is not UNSET_ARG:
            return default
        raise NoResults(f"Key '{key}' not found in any source")

    def explain(self, key: str) -> List[str]:
        """Explain which sources were consulted for ``key``.

        Args:
            key: Top-level key or dotted path.

        Returns:
            Human-readable report lines.
        """
        report: List[str] = []
        self._query_first(key, report=report)
        return report

    def query(self, key: str, mode: Optional[str] = None, report: Optional[List[str]] = None) -> Any:
        """Query a key across sources.

        Args:
            key: Top-level key or dotted path.
            mode: ``first`` (default) returns the winning value; ``all`` returns
                every hit as a list.
            report: Optional list appended with lookup steps.

        Returns:
            Winning value, or list of values when ``mode='all'``.

        Raises:
            NoResults: If nothing is found.
            ViewError: If mode is unknown.
        """
        mode = mode or "first"
        report = report if report is not None else []

        if mode == "first":
            value = self._query_first(key, report=report)
            if value is UNSET_ARG:
                raise NoResults(f"Key '{key}' not found in any source")
            return value

        if mode == "all":
            values = self._query_all(key, report=report)
            if not values:
                raise NoResults(f"Key '{key}' not found in any source")
            return values

        raise ViewError(f"Unknown query mode {mode!r}; use 'first' or 'all'")

    def _query_first(self, key: str, report: List[str]) -> Any:
        """Walk sources high-to-low; return first set value or UNSET_ARG."""
        for source in self.get_ordered_sources():
            report.append(f"Querying '{key}' from {source.name}")
            data = source.load()
            value = _lookup_path(data, key)
            if value is UNSET_ARG:
                report.append(f"  Not found '{key}' from {source.name}")
                continue
            report.append(f"  Found '{key}' from {source.name}")
            return value
        return UNSET_ARG

    def _query_all(self, key: str, report: List[str]) -> List[Any]:
        """Walk sources high-to-low; collect all set values."""
        values: List[Any] = []
        for source in self.get_ordered_sources():
            report.append(f"Querying '{key}' from {source.name}")
            data = source.load()
            value = _lookup_path(data, key)
            if value is UNSET_ARG:
                report.append(f"  Not found '{key}' from {source.name}")
                continue
            report.append(f"  Found '{key}' from {source.name}")
            values.append(value)
        return values
