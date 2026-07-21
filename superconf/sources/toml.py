"""TOML source converter."""

from __future__ import annotations

from typing import Any, Mapping

from superconf.sources.base import (
    DataDict,
    SourceDumpError,
    SourceLoadError,
    TextFileSource,
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


class TomlSource(TextFileSource):
    """Source that loads/dumps TOML text or files.

    Loading uses ``tomllib`` (Python 3.11+) or the ``tomli`` package.
    Dumping uses ``tomli-w`` when installed.

    Args:
        name: Unique source name.
        data: TOML string, filesystem path, or None.
        path: Optional path (alternative to ``data`` when loading a file).
        help: Optional description.
    """

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
        return self._as_root_dict(parsed, "TOML")

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
