"""Base types for configuration data sources."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Mapping, Optional, Union

from superconf.common import read_file

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


class TextFileSource(BaseSource):
    """Base for sources that load from a text string or filesystem path.

    Args:
        name: Unique source name.
        data: Format text, filesystem path, or None.
        path: Optional path (alternative to ``data`` when loading a file).
        help: Optional description.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        name: str,
        data: Union[str, Path, None] = None,
        *,
        path: Union[str, Path, None] = None,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, help=help)
        self._data = data
        self._path = path

    def _read_raw(self) -> str:
        """Return text from ``data`` or ``path``.

        Returns:
            Raw format text.

        Raises:
            SourceLoadError: If neither input is set.
        """
        if self._path is not None:
            return read_file(str(self._path))
        if self._data is None:
            raise SourceLoadError(
                f"{self.__class__.__name__} {self.name!r} has no data or path to load"
            )
        path_candidate = Path(str(self._data))
        if path_candidate.is_file():
            return read_file(str(path_candidate))
        return str(self._data)

    def load(self) -> DataDict:
        """Load data as a nested dict.

        Subclasses must implement format-specific parsing.

        Returns:
            Nested configuration dictionary.
        """
        raise NotImplementedError()

    def dump(self, data: Mapping[str, Any]) -> Union[str, DataDict, None]:
        """Dump a nested dict to this source's format.

        Subclasses must implement format-specific serialization.

        Args:
            data: Nested configuration dictionary.

        Returns:
            Format-specific representation (string, dict, or None).
        """
        raise NotImplementedError()

    def _as_root_dict(self, parsed: Any, root_label: str) -> DataDict:
        """Normalize parsed content to a root dict.

        Args:
            parsed: Value returned by the format parser.
            root_label: Human-readable format label for errors (e.g. ``JSON``).

        Returns:
            Empty dict if ``parsed`` is None, otherwise ``parsed`` as a dict.

        Raises:
            SourceLoadError: If ``parsed`` is not a dict.
        """
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise SourceLoadError(
                f"{root_label} root must be a dict, got {type(parsed).__name__}"
            )
        return parsed


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
