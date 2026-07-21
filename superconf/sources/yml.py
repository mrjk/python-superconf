"""YAML source converter."""

from __future__ import annotations

from typing import Any, Mapping

from superconf.common import from_yaml, to_yaml
from superconf.sources.base import DataDict, TextFileSource


class YamlSource(TextFileSource):
    """Source that loads/dumps YAML text or files.

    Args:
        name: Unique source name.
        data: YAML string, filesystem path, or None.
        path: Optional path (alternative to ``data`` when loading a file).
        help: Optional description.
    """

    def load(self) -> DataDict:
        """Parse YAML from string or file into a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            SourceLoadError: If no input is configured or YAML is not a dict.
        """
        return self._as_root_dict(from_yaml(self._read_raw()), "YAML")

    def dump(self, data: Mapping[str, Any]) -> str:
        """Serialize a nested dict to a YAML string.

        Args:
            data: Nested configuration dictionary.

        Returns:
            YAML text.
        """
        return to_yaml(dict(data))
