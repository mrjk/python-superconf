"""Unit tests for the anchors module.

This module contains test cases for the PathAnchor and FileAnchor classes,
covering path resolution, mode handling, and anchor chain functionality.
"""

# pylint: skip-file


import os
import pytest
from superconf.anchors import PathAnchor, FileAnchor


@pytest.fixture
def fake_root():
    """Fixture providing a fake root directory path."""
    return "/fake/root"


@pytest.fixture
def project_anchor(fake_root):
    """Fixture providing a base project anchor."""
    return PathAnchor(os.path.join(fake_root, "project"))


class TestPathAnchor:
    def test_basic_path_handling(self):
        """Test basic path handling without anchors."""
        path = PathAnchor("/simple/path")
        assert path.get_dir() == "/simple/path"
        assert path.get_dir(mode="abs") == "/simple/path"

    def test_relative_path_handling(self):
        """Test relative path handling."""
        path = PathAnchor("relative/path", mode="rel")
        assert path.get_dir(start="/base") == "relative/path"
        assert path.get_dir(mode="abs") == os.path.abspath("relative/path")

    def test_anchored_paths(self, project_anchor):
        """Test paths with anchor points."""
        subdir = PathAnchor("subdir", anchor=project_anchor)
        assert subdir.get_dir(mode="abs") == "/fake/root/project/subdir"
        assert subdir.get_dir(mode="rel", start="/fake/root") == "project/subdir"

    def test_path_cleaning(self, project_anchor):
        """Test path normalization."""
        messy_path = PathAnchor("subdir/../other/./path", anchor=project_anchor)
        assert messy_path.get_dir(clean=True) == "/fake/root/project/other/path"

    def test_mode_inheritance(self, project_anchor):
        """Test mode inheritance through anchor chain."""
        root = PathAnchor("/root", mode="rel")
        child = PathAnchor("child", anchor=root)
        assert child.get_mode() == "rel"

    def test_get_parents(self, project_anchor):
        """Test retrieving anchor chain."""
        child = PathAnchor("child", anchor=project_anchor)
        grandchild = PathAnchor("grandchild", anchor=child)

        parents = grandchild.get_parents()
        assert len(parents) == 2
        assert parents[0] == child
        assert parents[1] == project_anchor

    def test_invalid_mode(self):
        """Test handling of invalid modes."""
        path = PathAnchor("/test/path")
        with pytest.raises(ValueError):
            path.get_dir(mode="invalid")


class TestFileAnchor:
    def test_basic_file_handling(self):
        """Test basic file path handling."""
        file = FileAnchor("/path/to/file.txt")
        assert file.get_file() == "file.txt"
        assert file.get_dir() == "/path/to"
        assert file.get_path() == "/path/to/file.txt"

    def test_separate_components(self):
        """Test initialization with separate directory and filename."""
        file = FileAnchor("", directory="/path/to", filename="file.txt")
        assert file.get_file() == "file.txt"
        assert file.get_dir() == "/path/to"
        assert file.get_path() == "/path/to/file.txt"

    def test_anchored_file(self, project_anchor):
        """Test file paths with anchor points."""
        config = FileAnchor("config.yml", anchor=project_anchor)
        assert config.get_path() == "/fake/root/project/config.yml"
        assert config.get_file() == "config.yml"
        assert config.get_dir() == "/fake/root/project/"

    def test_nested_file_paths(self, project_anchor):
        """Test nested file paths with anchors."""
        config_dir = PathAnchor("config", anchor=project_anchor)
        config_file = FileAnchor("settings.yml", anchor=config_dir)

        assert config_file.get_path() == "config/settings.yml"
        assert (
            config_file.get_path(mode="rel", start="/fake/root")
            == "config/settings.yml"
        )

    def test_file_path_cleaning(self, project_anchor):
        """Test file path normalization."""
        messy_file = FileAnchor("subdir/../config/./file.txt", anchor=project_anchor)
        assert messy_file.get_path(clean=True) == "/fake/root/project/config/file.txt"
