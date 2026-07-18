"""Unit tests for multi-source View precedence and materialize."""

import pytest

from superconf.sources import DictSource, EnvSource, YamlSource
from superconf.views import (
    TWELVE_FACTOR_ORDER,
    NoResults,
    View,
    ViewOrderError,
)


pytestmark = pytest.mark.unit


def test_view_first_wins_and_materialize():
    """Higher-priority sources win; nested dicts merge deeply."""
    view = View(order=TWELVE_FACTOR_ORDER)
    view.add(DictSource("defaults", {"name": "base", "db": {"host": "local", "port": 1}}))
    view.add(DictSource("file", {"db": {"port": 2}, "tags": ["a"]}))
    view.add(EnvSource("env", prefix="APP", environ={"APP__DB__HOST": "remote"}))
    view.add(DictSource("cli", {"tags": ["cli"]}))

    assert view.get("tags") == ["cli"]
    assert view.get("name") == "base"
    assert view.get("db.host") == "remote"

    merged = view.materialize()
    assert merged == {
        "name": "base",
        "db": {"host": "remote", "port": 2},
        "tags": ["cli"],
    }


def test_view_explain_and_query_all():
    """explain/report and mode=all return lookup details."""
    view = View()
    view.add(DictSource("defaults", {"name": "base"}))
    view.add(DictSource("cli", {"name": "override"}))
    view.set_order(["cli", "defaults"])

    report = view.explain("name")
    assert any("Found" in line and "cli" in line for line in report)

    values = view.query("name", mode="all")
    assert values == ["override", "base"]


def test_view_missing_key_raises():
    """Missing keys raise NoResults unless a default is given."""
    view = View()
    view.add(DictSource("defaults", {"name": "base"}))
    with pytest.raises(NoResults):
        view.get("missing")
    assert view.get("missing", default=None) is None


def test_view_rejects_duplicate_source_and_order():
    """Duplicate source names and duplicate order entries fail."""
    view = View()
    view.add(DictSource("cli", {}))
    with pytest.raises(ViewOrderError):
        view.add(DictSource("cli", {"x": 1}))
    with pytest.raises(ViewOrderError):
        view.set_order(["cli", "cli"])


def test_view_preset_order_rejects_unknown_source_name():
    """Sources must match preset order names when provided."""
    view = View(order=["cli", "env"])
    with pytest.raises(ViewOrderError):
        view.add(DictSource("file", {}))


def test_view_with_yaml_layer(tmp_path):
    """YAML file source participates in precedence."""
    path = tmp_path / "app.yml"
    path.write_text("name: from-file\nworkers: 3\n", encoding="utf-8")

    view = View(order=["cli", "file", "defaults"])
    view.add(DictSource("defaults", {"name": "default", "workers": 1}))
    view.add(YamlSource("file", path=path))
    view.add(DictSource("cli", {"workers": 9}))

    assert view.materialize() == {"name": "from-file", "workers": 9}
