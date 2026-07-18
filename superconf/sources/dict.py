"""In-memory dict source converter."""

from __future__ import annotations

from typing import Any, Mapping, Optional, Union

from superconf.sources.base import BaseSource, DataDict, DataFactory, resolve_mapping


class DictSource(BaseSource):
    """Source backed by an in-memory mapping (or factory).

    Useful for CLI overlays and already-parsed data.

    Args:
        name: Unique source name.
        data: Mapping or zero-arg callable returning a mapping.
        help: Optional description.
    """

    # pylint: disable=redefined-builtin
    def __init__(
        self,
        name: str,
        data: Union[Mapping[str, Any], DataFactory, None] = None,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, help=help)
        self._data = data

    def load(self) -> DataDict:
        """Return a copy of the configured mapping.

        Returns:
            Nested configuration dictionary.
        """
        return resolve_mapping(self._data)

    def dump(self, data: Mapping[str, Any]) -> DataDict:
        """Return a plain dict copy of ``data``.

        Args:
            data: Nested configuration dictionary.

        Returns:
            Shallow-copied dict.
        """
        return dict(data)
