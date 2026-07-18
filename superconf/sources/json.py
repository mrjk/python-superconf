"""JSON source converter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from superconf.common import from_json, read_file, to_json
from superconf.sources.base import BaseSource, DataDict, SourceLoadError


class JsonSource(BaseSource):
    """Source that loads/dumps JSON text or files.

    Args:
        name: Unique source name.
        data: JSON string, filesystem path, or None.
        path: Optional path (alternative to ``data`` when loading a file).
        nice: Pretty-print JSON on dump when True.
        help: Optional description.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        name: str,
        data: Union[str, Path, None] = None,
        *,
        path: Union[str, Path, None] = None,
        nice: bool = True,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, help=help)
        self._data = data
        self._path = path
        self.nice = nice

    def load(self) -> DataDict:
        """Parse JSON from string or file into a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            SourceLoadError: If no input is configured or JSON is not a dict.
        """
        raw = self._read_raw()
        parsed = from_json(raw)
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise SourceLoadError(
                f"JSON root must be an object/dict, got {type(parsed).__name__}"
            )
        return parsed

    def dump(self, data: Mapping[str, Any]) -> str:
        """Serialize a nested dict to a JSON string.

        Args:
            data: Nested configuration dictionary.

        Returns:
            JSON text.
        """
        return to_json(dict(data), nice=self.nice)

    def _read_raw(self) -> str:
        """Return JSON text from ``data`` or ``path``.

        Returns:
            Raw JSON string.

        Raises:
            SourceLoadError: If neither input is set.
        """
        if self._path is not None:
            return read_file(str(self._path))
        if self._data is None:
            raise SourceLoadError(
                f"JsonSource {self.name!r} has no data or path to load"
            )
        path_candidate = Path(str(self._data))
        if path_candidate.is_file():
            return read_file(str(path_candidate))
        return str(self._data)
