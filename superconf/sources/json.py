"""JSON source converter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from superconf.common import from_json, to_json
from superconf.sources.base import DataDict, TextFileSource


class JsonSource(TextFileSource):
    """Source that loads/dumps JSON text or files.

    Args:
        name: Unique source name.
        data: JSON string, filesystem path, or None.
        path: Optional path (alternative to ``data`` when loading a file).
        nice: Pretty-print JSON on dump when True.
        help: Optional description.
    """

    def __init__(  # pylint: disable=redefined-builtin,too-many-arguments
        self,
        name: str,
        data: Union[str, Path, None] = None,
        *,
        path: Union[str, Path, None] = None,
        nice: bool = True,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, data, path=path, help=help)
        self.nice = nice

    def load(self) -> DataDict:
        """Parse JSON from string or file into a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            SourceLoadError: If no input is configured or JSON is not a dict.
        """
        return self._as_root_dict(from_json(self._read_raw()), "JSON")

    def dump(self, data: Mapping[str, Any]) -> str:
        """Serialize a nested dict to a JSON string.

        Args:
            data: Nested configuration dictionary.

        Returns:
            JSON text.
        """
        return to_json(dict(data), nice=self.nice)
