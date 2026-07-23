"""Helpers to load a typed config from 12-factor layered sources.

Wires schema defaults, optional file, environment (``PREFIX__PATH``), and an
optional CLI dict through ``View`` with ``TWELVE_FACTOR_ORDER`` precedence.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Optional, Sequence, Type, TypeVar, Union

from superconf.sources import (
    ConfigSource,
    DictSource,
    EnvSource,
    JsonSource,
    TomlSource,
    YamlSource,
)
from superconf.sources.base import BaseSource
from superconf.views import TWELVE_FACTOR_ORDER, View

ConfigT = TypeVar("ConfigT")
PathLike = Union[str, Path]


class TwelveFactorError(ValueError):
    """Raised when 12-factor loading cannot be configured."""


def _resolve_env_prefix(
    config_cls: type,
    env_prefix: Optional[str],
) -> Optional[str]:
    """Return an env prefix from the argument or ``Meta.env_prefix``.

    Args:
        config_cls: Configuration class that may define ``Meta.env_prefix``.
        env_prefix: Explicit prefix; wins when set.

    Returns:
        Resolved prefix string, or ``None`` if neither source provides one.
    """
    if env_prefix is not None:
        cleaned = str(env_prefix).strip()
        return cleaned or None
    meta = getattr(config_cls, "Meta", None)
    if meta is None:
        return None
    meta_prefix = getattr(meta, "env_prefix", None)
    if meta_prefix is None:
        return None
    cleaned = str(meta_prefix).strip()
    return cleaned or None


def _file_source(path: PathLike) -> BaseSource:
    """Build a file source from a path suffix.

    Args:
        path: Filesystem path to a YAML, JSON, or TOML file.

    Returns:
        Named ``file`` source instance.

    Raises:
        TwelveFactorError: If the suffix is not supported.
    """
    resolved = Path(path)
    suffix = resolved.suffix.lower()
    if suffix in (".yml", ".yaml"):
        return YamlSource("file", path=resolved)
    if suffix == ".json":
        return JsonSource("file", path=resolved)
    if suffix == ".toml":
        return TomlSource("file", path=resolved)
    raise TwelveFactorError(
        f"Unsupported config file suffix {suffix!r} for {resolved}; "
        "use .yml, .yaml, .json, or .toml"
    )


# Keyword-only public API: layer knobs stay explicit (not a options bag).
# pylint: disable-next=too-many-arguments
def build_12factor_view(
    config_cls: type,
    *,
    env_prefix: Optional[str] = None,
    file: Optional[PathLike] = None,
    cli: Optional[Mapping[str, Any]] = None,
    environ: Optional[Mapping[str, str]] = None,
    order: Optional[Sequence[str]] = None,
) -> View:
    """Build a ``View`` with defaults, optional file/env/cli layers.

    Args:
        config_cls: Configuration class used for schema defaults.
        env_prefix: Env var prefix (e.g. ``APP``). Falls back to
            ``Meta.env_prefix`` when omitted.
        file: Optional path to a YAML/JSON/TOML config file.
        cli: Optional mapping of CLI overrides (highest priority).
        environ: Optional env mapping (defaults to ``os.environ`` in
            ``EnvSource`` when omitted).
        order: Source names, highest priority first. Defaults to
            ``TWELVE_FACTOR_ORDER``.

    Returns:
        Configured ``View`` ready for ``materialize()`` / ``explain()``.
    """
    view = View(order=list(order) if order is not None else list(TWELVE_FACTOR_ORDER))
    view.add(ConfigSource("defaults", config_cls(), nodefaults=False))

    if file is not None:
        view.add(_file_source(file))

    prefix = _resolve_env_prefix(config_cls, env_prefix)
    if prefix is not None:
        view.add(EnvSource("env", prefix=prefix, environ=environ))

    if cli is not None:
        view.add(DictSource("cli", cli))

    return view


# pylint: disable-next=too-many-arguments
def load_12factor(
    config_cls: Type[ConfigT],
    *,
    env_prefix: Optional[str] = None,
    file: Optional[PathLike] = None,
    cli: Optional[Mapping[str, Any]] = None,
    environ: Optional[Mapping[str, str]] = None,
    order: Optional[Sequence[str]] = None,
) -> ConfigT:
    """Load a typed config from layered 12-factor sources.

    Precedence (highest first): ``cli`` → ``env`` → ``file`` → ``defaults``.

    Args:
        config_cls: Configuration class to instantiate.
        env_prefix: Env var prefix (e.g. ``APP``). Falls back to
            ``Meta.env_prefix`` when omitted. Env layer is skipped if neither
            is set.
        file: Optional path to a YAML/JSON/TOML config file.
        cli: Optional mapping of CLI overrides.
        environ: Optional env mapping for tests; defaults to ``os.environ``.
        order: Optional custom source order (highest first).

    Returns:
        Instance of ``config_cls`` with merged, cast values.
    """
    view = build_12factor_view(
        config_cls,
        env_prefix=env_prefix,
        file=file,
        cli=cli,
        environ=environ,
        order=order,
    )
    return config_cls(value=view.materialize())


# Developer-facing alias (not a ConfigurationObj method — keep core free of this).
from_12factor = load_12factor
