"""Pure environment-variable codec: nested dict <-> PREFIX__PATH keys.

Standalone utility (no SuperConf types). Expand flattens env mappings into
nested dicts/lists; flatten does the reverse. Designed to be extractable.
"""

from __future__ import annotations

from typing import Any, Mapping, Union

EnvMapping = Mapping[str, str]
NestedData = Union[dict[str, Any], list[Any]]


class CodecEnvError(ValueError):
    """Base error for environment codec failures."""


class CodecEnvPrefixError(CodecEnvError):
    """Raised when the env prefix is missing or invalid."""


class CodecEnvConflictError(CodecEnvError):
    """Raised when a leaf and a container claim the same path."""


def _normalize_prefix(prefix: str, separator: str) -> str:
    """Return a stripped uppercase prefix without a trailing separator.

    Args:
        prefix: Required env prefix (e.g. ``APP`` or ``APP__``).
        separator: Path separator between segments.

    Returns:
        Normalized prefix without a trailing separator.

    Raises:
        CodecEnvPrefixError: If prefix is empty after strip.
    """
    cleaned = prefix.strip()
    if not cleaned:
        raise CodecEnvPrefixError("Environment prefix must be a non-empty string")
    if cleaned.endswith(separator):
        cleaned = cleaned[: -len(separator)]
    if not cleaned:
        raise CodecEnvPrefixError("Environment prefix must be a non-empty string")
    return cleaned.upper()


def _is_index(segment: str) -> bool:
    """Return True if segment is an all-digit list index."""
    return bool(segment) and segment.isdigit()


def _ensure_container(
    parent: NestedData,
    key: Union[str, int],
    child_is_index: bool,
    path: str,
) -> NestedData:
    """Ensure parent[key] is a dict or list matching the next segment type.

    Args:
        parent: Current container (dict or list).
        key: Key or index into parent.
        child_is_index: True if the next segment is a list index.
        path: Full env key path for error messages.

    Returns:
        The child container (created if missing).

    Raises:
        CodecEnvConflictError: If an existing leaf blocks a container.
    """
    expected: type = list if child_is_index else dict

    if isinstance(parent, dict):
        assert isinstance(key, str)
        if key not in parent:
            parent[key] = [] if child_is_index else {}
        child = parent[key]
    else:
        assert isinstance(parent, list)
        assert isinstance(key, int)
        while len(parent) <= key:
            parent.append(None)
        child = parent[key]
        if child is None:
            parent[key] = [] if child_is_index else {}
            child = parent[key]

    if isinstance(child, expected):
        return child

    if isinstance(child, (dict, list)):
        got = type(child).__name__
        want = expected.__name__
        raise CodecEnvConflictError(
            f"Path conflict at '{path}': existing {got} incompatible with {want}"
        )

    raise CodecEnvConflictError(
        f"Path conflict at '{path}': leaf value {child!r} blocks container"
    )


def _set_leaf(
    parent: NestedData,
    key: Union[str, int],
    value: str,
    path: str,
) -> None:
    """Set a leaf string on parent, rejecting container overwrite.

    Args:
        parent: Current container (dict or list).
        key: Key or index into parent.
        value: Leaf string value from the environment.
        path: Full env key path for error messages.

    Raises:
        CodecEnvConflictError: If a container already exists at this path.
    """
    if isinstance(parent, dict):
        assert isinstance(key, str)
        existing = parent.get(key, None)
        if isinstance(existing, (dict, list)):
            raise CodecEnvConflictError(
                f"Path conflict at '{path}': container blocks leaf {value!r}"
            )
        parent[key] = value
        return

    assert isinstance(parent, list)
    assert isinstance(key, int)
    while len(parent) <= key:
        parent.append(None)
    existing = parent[key]
    if isinstance(existing, (dict, list)):
        raise CodecEnvConflictError(
            f"Path conflict at '{path}': container blocks leaf {value!r}"
        )
    parent[key] = value


def _compact_lists(node: Any) -> Any:
    """Recursively drop None holes from lists (missing indexes).

    Args:
        node: Nested dict/list/leaf structure.

    Returns:
        Structure with list holes removed; dicts walked recursively.
    """
    if isinstance(node, dict):
        return {key: _compact_lists(val) for key, val in node.items()}
    if isinstance(node, list):
        return [_compact_lists(item) for item in node if item is not None]
    return node


def _apply_env_path(
    root: dict[str, Any],
    segments: list[str],
    value: str,
    *,
    norm_prefix: str,
    separator: str,
    lowercase_keys: bool,
) -> None:
    """Apply one env path (segment list) onto the nested root dict.

    Args:
        root: Destination nested dict (mutated in place).
        segments: Uppercase path segments after the prefix.
        value: Leaf string value.
        norm_prefix: Normalized uppercase prefix.
        separator: Path separator.
        lowercase_keys: Lowercase non-index segments when True.

    Raises:
        CodecEnvConflictError: On leaf/container path conflicts.
    """
    parent: NestedData = root
    path_parts: list[str] = []

    for index, segment in enumerate(segments):
        is_last = index == len(segments) - 1
        path_parts.append(segment)
        path = separator.join([norm_prefix, *path_parts])

        if _is_index(segment):
            key: Union[str, int] = int(segment)
        else:
            key = segment.lower() if lowercase_keys else segment

        if is_last:
            _set_leaf(parent, key, value, path)
            return

        next_is_index = _is_index(segments[index + 1])
        parent = _ensure_container(parent, key, next_is_index, path)


def expand_env(
    environ: EnvMapping,
    prefix: str,
    separator: str = "__",
    *,
    lowercase_keys: bool = True,
) -> dict[str, Any]:
    """Expand ``PREFIX__PATH`` env vars into a nested dict.

    Matching keys are case-insensitive on the prefix. Path segments that are
    all digits become list indexes; other segments become dict keys. Missing
    list indexes are dropped (compact), by design, with no warning. Values
    remain strings.

    Args:
        environ: Mapping of environment variables (e.g. ``os.environ``).
        prefix: Required prefix (``APP`` or ``APP__``).
        separator: Segment separator (default ``__``).
        lowercase_keys: Lowercase non-index path segments in the result.

    Returns:
        Nested dict built from matching variables.

    Raises:
        CodecEnvPrefixError: If prefix is empty.
        CodecEnvConflictError: If leaf and container paths collide.
    """
    norm_prefix = _normalize_prefix(prefix, separator)
    head = norm_prefix + separator
    root: dict[str, Any] = {}

    for raw_key, raw_value in environ.items():
        env_key = str(raw_key).upper()
        if not env_key.startswith(head):
            continue
        remainder = env_key[len(head) :]
        if not remainder:
            raise CodecEnvConflictError(
                f"Environment key '{raw_key}' matches prefix only; need a path"
            )

        segments = remainder.split(separator)
        if any(not segment for segment in segments):
            raise CodecEnvConflictError(
                f"Environment key '{raw_key}' has an empty path segment"
            )

        _apply_env_path(
            root,
            segments,
            str(raw_value),
            norm_prefix=norm_prefix,
            separator=separator,
            lowercase_keys=lowercase_keys,
        )

    return _compact_lists(root)


def _format_env_value(value: Any) -> str:
    """Convert a leaf Python value to an env string.

    Args:
        value: Scalar leaf value.

    Returns:
        String form; booleans use lowercase ``true`` / ``false``.
    """
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def flatten_env(
    data: Mapping[str, Any],
    prefix: str,
    separator: str = "__",
    *,
    skip_none: bool = True,
    uppercase_keys: bool = True,
) -> dict[str, str]:
    """Flatten a nested dict into ``PREFIX__PATH`` env entries.

    Args:
        data: Nested mapping (dicts and lists).
        prefix: Required prefix (``APP`` or ``APP__``).
        separator: Segment separator (default ``__``).
        skip_none: If True (default), omit keys whose value is ``None``.
            If False, emit an empty string for ``None``.
        uppercase_keys: Uppercase the full env key (default True).

    Returns:
        Flat dict of env key → string value, sorted by key.

    Raises:
        CodecEnvPrefixError: If prefix is empty.
        CodecEnvConflictError: If a non-dict/list/scalar leaf type appears.
    """
    norm_prefix = _normalize_prefix(prefix, separator)
    out: dict[str, str] = {}

    def walk(node: Any, parts: list[str]) -> None:
        if node is None:
            if skip_none:
                return
            key = separator.join(parts)
            if uppercase_keys:
                key = key.upper()
            out[key] = ""
            return

        if isinstance(node, Mapping):
            for key, val in node.items():
                walk(val, parts + [str(key)])
            return

        if isinstance(node, list):
            for index, val in enumerate(node):
                walk(val, parts + [str(index)])
            return

        key = separator.join(parts)
        if uppercase_keys:
            key = key.upper()
        out[key] = _format_env_value(node)

    if not isinstance(data, Mapping):
        raise CodecEnvConflictError("flatten_env expects a mapping at the root")

    walk(data, [norm_prefix])
    return dict(sorted(out.items()))


def to_dotenv(
    env_map: Mapping[str, str],
    *,
    export: bool = False,
) -> str:
    """Render a flat env map as dotenv or shell ``export`` lines.

    Args:
        env_map: Flat ``KEY`` → ``value`` mapping.
        export: If True, prefix lines with ``export ``.

    Returns:
        Newline-terminated text block (empty string if no keys).
    """
    lines: list[str] = []
    prefix = "export " if export else ""
    for key, value in sorted(env_map.items()):
        lines.append(f"{prefix}{key}={_dotenv_quote(value)}")
    return "\n".join(lines) + ("\n" if lines else "")


def _dotenv_quote(value: str) -> str:
    """Quote a value for dotenv if it needs escaping.

    Args:
        value: Raw string value.

    Returns:
        Possibly double-quoted string safe for dotenv-style files.
    """
    if value == "":
        return '""'
    needs_quote = any(char in value for char in ' \t\n\r#"\'\\')
    if not needs_quote:
        return value
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\n", "\\n")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'
