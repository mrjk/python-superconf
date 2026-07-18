"""Environment-variable source converter."""

from __future__ import annotations

import os
from typing import Any, Mapping, Optional, Union

from superconf.lib.codec_env import expand_env, flatten_env, to_dotenv
from superconf.sources.base import BaseSource, DataDict, SourceDumpError


class EnvSource(BaseSource):
    """Source that converts ``PREFIX__PATH`` environment variables.

    Args:
        name: Unique source name.
        prefix: Required env prefix (e.g. ``APP``).
        environ: Optional mapping (defaults to ``os.environ``).
        separator: Path separator (default ``__``).
        skip_none: When dumping, omit ``None`` values if True.
        help: Optional description.
    """

    def __init__(  # pylint: disable=redefined-builtin,too-many-arguments
        self,
        name: str,
        prefix: str,
        environ: Optional[Mapping[str, str]] = None,
        *,
        separator: str = "__",
        skip_none: bool = True,
        help: Optional[str] = None,
    ) -> None:
        super().__init__(name, help=help)
        self.prefix = prefix
        self.separator = separator
        self.skip_none = skip_none
        self._environ = environ

    def load(self) -> DataDict:
        """Expand matching environment variables into a nested dict.

        Returns:
            Nested configuration dictionary (values as strings).
        """
        environ = self._environ if self._environ is not None else os.environ
        return expand_env(environ, prefix=self.prefix, separator=self.separator)

    def dump(
        self,
        data: Mapping[str, Any],
        *,
        fmt: str = "dict",
        skip_none: Optional[bool] = None,
    ) -> Union[DataDict, str]:
        """Flatten a nested dict to env keys.

        Args:
            data: Nested configuration dictionary.
            fmt: ``dict``, ``dotenv``, or ``exports``.
            skip_none: Override constructor ``skip_none`` when set.

        Returns:
            Flat env dict, or dotenv/export text.

        Raises:
            SourceDumpError: If ``fmt`` is unknown.
        """
        omit_none = self.skip_none if skip_none is None else skip_none
        flat = flatten_env(
            data,
            prefix=self.prefix,
            separator=self.separator,
            skip_none=omit_none,
        )
        if fmt == "dict":
            return flat
        if fmt == "dotenv":
            return to_dotenv(flat, export=False)
        if fmt == "exports":
            return to_dotenv(flat, export=True)
        raise SourceDumpError(
            f"Unknown env dump format {fmt!r}; use dict, dotenv, or exports"
        )
