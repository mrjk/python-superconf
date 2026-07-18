"""Base types for configuration data sources."""

from __future__ import annotations

from typing import Any, Callable, Mapping, Optional, Union

DataDict = dict[str, Any]
DataFactory = Callable[[], Mapping[str, Any]]


class SourceError(Exception):
    """Base error for source converters."""


class SourceLoadError(SourceError):
    """Raised when a source cannot load data."""


class SourceDumpError(SourceError):
    """Raised when a source cannot dump data."""


class BaseSource:
    """Base converter between an external format and a nested dict.

    Args:
        name: Unique source name used by ``View`` ordering.
        help: Optional description of this source.
    """

    # pylint: disable=redefined-builtin
    def __init__(self, name: str, help: Optional[str] = None) -> None:
        if not name or not str(name).strip():
            raise SourceError("Source name must be a non-empty string")
        self.name = str(name).strip()
        self.help = help

    def load(self) -> DataDict:
        """Load data as a nested dict.

        Returns:
            Nested configuration dictionary.
        """
        raise NotImplementedError()

    def dump(self, data: Mapping[str, Any]) -> Union[str, DataDict, None]:
        """Dump a nested dict to this source's format.

        Args:
            data: Nested configuration dictionary.

        Returns:
            Format-specific representation (string, dict, or None).
        """
        raise NotImplementedError()

    def get_help(self) -> str:
        """Return help text for this source.

        Returns:
            Configured help string, or a default label.
        """
        if not self.help:
            return f"Source {self.name}"
        return self.help

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name!r})"


def resolve_mapping(
    data: Union[Mapping[str, Any], DataFactory, None],
) -> DataDict:
    """Normalize a mapping or factory into a plain dict.

    Args:
        data: Mapping, zero-arg callable returning a mapping, or None.

    Returns:
        A shallow-copied dict (empty if data is None).

    Raises:
        SourceLoadError: If the value is not a mapping.
    """
    if data is None:
        return {}
    if callable(data):
        data = data()
    if data is None:
        return {}
    if not isinstance(data, Mapping):
        raise SourceLoadError(
            f"Expected a mapping, got {type(data).__name__}: {data!r}"
        )
    return dict(data)
