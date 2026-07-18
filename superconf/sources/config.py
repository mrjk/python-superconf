"""ConfigurationObj / container source converter."""

from __future__ import annotations

from typing import Any, Mapping, Optional

from superconf.common import NOT_SET
from superconf.sources.base import (
    BaseSource,
    DataDict,
    SourceDumpError,
    SourceLoadError,
)


def _strip_unset(node: Any) -> Any:
    """Remove NOT_SET sentinels from a nested structure.

    Args:
        node: Nested value possibly containing NOT_SET leaves.

    Returns:
        Cleaned structure, or ``None`` if the node itself is unset.
    """
    if isinstance(node, NOT_SET.type):
        return None
    if isinstance(node, Mapping):
        out: DataDict = {}
        for key, val in node.items():
            cleaned = _strip_unset(val)
            if cleaned is None and isinstance(val, NOT_SET.type):
                continue
            out[key] = cleaned
        return out
    if isinstance(node, list):
        return [_strip_unset(item) for item in node]
    return node


class ConfigSource(BaseSource):
    """Source backed by a SuperConf configuration instance.

    Args:
        name: Unique source name.
        config: Object with ``get_value`` / optional ``set_value``.
        nodefaults: Passed to ``get_value`` (True = only explicitly set values).
        help: Optional description.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        name: str,
        config: Any,
        *,
        nodefaults: bool = True,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, help=help)
        if not hasattr(config, "get_value"):
            raise SourceLoadError(
                "ConfigSource requires an object with a get_value() method"
            )
        self._config = config
        self.nodefaults = nodefaults

    def load(self) -> DataDict:
        """Load values from the configuration instance.

        Returns:
            Nested dict with NOT_SET entries stripped.
        """
        raw = self._config.get_value(nodefaults=self.nodefaults)
        if raw is None or isinstance(raw, NOT_SET.type):
            return {}
        if not isinstance(raw, Mapping):
            raise SourceLoadError(
                f"ConfigSource expected a mapping from get_value(), "
                f"got {type(raw).__name__}"
            )
        cleaned = _strip_unset(raw)
        return cleaned if isinstance(cleaned, dict) else {}

    def dump(self, data: Mapping[str, Any]) -> DataDict:
        """Apply ``data`` onto the config via ``set_value`` when available.

        Args:
            data: Nested configuration dictionary.

        Returns:
            The data dict after applying (or as-is if read-only).

        Raises:
            SourceDumpError: If ``set_value`` is missing.
        """
        if not hasattr(self._config, "set_value"):
            raise SourceDumpError(
                f"ConfigSource {self.name!r} config has no set_value()"
            )
        self._config.set_value(dict(data))
        return dict(data)
