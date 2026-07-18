"""YAML source converter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from superconf.common import from_yaml, read_file, to_yaml
from superconf.sources.base import BaseSource, DataDict, SourceLoadError


class YamlSource(BaseSource):
    """Source that loads/dumps YAML text or files.

    Args:
        name: Unique source name.
        data: YAML string, filesystem path, or None.
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

    def load(self) -> DataDict:
        """Parse YAML from string or file into a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            SourceLoadError: If no input is configured or YAML is not a dict.
        """
        raw = self._read_raw()
        parsed = from_yaml(raw)
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise SourceLoadError(
                f"YAML root must be a mapping/dict, got {type(parsed).__name__}"
            )
        return parsed

    def dump(self, data: Mapping[str, Any]) -> str:
        """Serialize a nested dict to a YAML string.

        Args:
            data: Nested configuration dictionary.

        Returns:
            YAML text.
        """
        return to_yaml(dict(data))

    def _read_raw(self) -> str:
        """Return YAML text from ``data`` or ``path``.

        Returns:
            Raw YAML string.

        Raises:
            SourceLoadError: If neither input is set.
        """
        if self._path is not None:
            return read_file(str(self._path))
        if self._data is None:
            raise SourceLoadError(
                f"YamlSource {self.name!r} has no data or path to load"
            )
        path_candidate = Path(str(self._data))
        if path_candidate.is_file():
            return read_file(str(path_candidate))
        return str(self._data)
