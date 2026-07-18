"""TOML source converter."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Union

from superconf.common import read_file
from superconf.sources.base import (
    BaseSource,
    DataDict,
    SourceDumpError,
    SourceLoadError,
)


def _load_toml_module() -> Any:
    """Import tomllib (3.11+) or tomli.

    Returns:
        Module with ``loads`` for TOML text.

    Raises:
        SourceLoadError: If neither backend is available.
    """
    try:
        import tomllib  # pylint: disable=import-outside-toplevel

        return tomllib
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # pylint: disable=import-outside-toplevel

            return tomllib
        except ModuleNotFoundError as err:
            raise SourceLoadError(
                "TOML support requires Python 3.11+ (tomllib) or the 'tomli' package"
            ) from err


class TomlSource(BaseSource):
    """Source that loads/dumps TOML text or files.

    Loading uses ``tomllib`` (Python 3.11+) or the ``tomli`` package.
    Dumping uses ``tomli-w`` when installed.

    Args:
        name: Unique source name.
        data: TOML string, filesystem path, or None.
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
        """Parse TOML from string or file into a nested dict.

        Returns:
            Nested configuration dictionary.

        Raises:
            SourceLoadError: If no input is configured or backend is missing.
        """
        raw = self._read_raw()
        tomllib = _load_toml_module()
        # tomllib.loads expects str on tomli; tomllib (stdlib) wants str via loads
        # in 3.11+ loads accepts str. Prefer loads; fall back to loads on bytes.
        try:
            parsed = tomllib.loads(raw)
        except TypeError:
            parsed = tomllib.loads(raw.encode("utf-8"))
        if parsed is None:
            return {}
        if not isinstance(parsed, dict):
            raise SourceLoadError(
                f"TOML root must be a table/dict, got {type(parsed).__name__}"
            )
        return parsed

    def dump(self, data: Mapping[str, Any]) -> str:
        """Serialize a nested dict to TOML text via ``tomli-w``.

        Args:
            data: Nested configuration dictionary.

        Returns:
            TOML text.

        Raises:
            SourceDumpError: If ``tomli-w`` is not installed.
        """
        try:
            import tomli_w  # pylint: disable=import-outside-toplevel
        except ModuleNotFoundError as err:
            raise SourceDumpError("TOML dump requires the 'tomli-w' package") from err
        return tomli_w.dumps(dict(data))

    def _read_raw(self) -> str:
        """Return TOML text from ``data`` or ``path``.

        Returns:
            Raw TOML string.

        Raises:
            SourceLoadError: If neither input is set.
        """
        if self._path is not None:
            return read_file(str(self._path))
        if self._data is None:
            raise SourceLoadError(
                f"TomlSource {self.name!r} has no data or path to load"
            )
        path_candidate = Path(str(self._data))
        if path_candidate.is_file():
            return read_file(str(path_candidate))
        return str(self._data)
