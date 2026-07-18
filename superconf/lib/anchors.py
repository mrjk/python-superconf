"""Path anchoring and manipulation library for flexible path resolution.

This module provides classes for handling paths with parent points, allowing for flexible
path resolution relative to different base directories. It's particularly useful for
configuration management and file organization where paths need to be resolved relative
to different root directories.

Main Components:
    - PathAnchor: Base class for handling directory paths with parent points
    - FileAnchor: Extension of PathAnchor for handling file paths specifically

Key Features:
    - Path resolution relative to parent points
    - Support for both absolute and relative path modes
    - Chain of parent points for complex path hierarchies
    - Clean path normalization
    - Flexible path representation

Examples:
    Basic path anchoring:

    >>> project_dir = "/fake/prj"
    >>> root = PathAnchor(project_dir)
    >>> conf = PathAnchor("../../common_conf", parent=root, mode="abs")
    >>> inventory = PathAnchor("inventory/", parent=conf, mode=anchors.REL)
    >>> 
    >>> # Get paths in different modes
    >>> conf.get_dir()  # Returns absolute path
    '/fake/common_conf'
    >>> inventory.get_dir()  # Returns relative path
    '../../inventory'

    File handling:

        >>> root = PathAnchor("/fake/prj")
        >>> config_file = FileAnchor("subconf/myfile.yml", parent=root)
        >>> config_file.get_path()  # Full path
        '/fake/prj/subconf/myfile.yml'
        >>> config_file.get_file()  # Just filename
        'myfile.yml'
        >>> config_file.get_dir()   # Just directory
        '/fake/prj/subconf'

    Complex path resolution:

        >>> project = PathAnchor("/fake_root/project")
        >>> path = PathAnchor("subdir2/../../subdir2/file", parent=project)
        >>> path.get_dir(clean=True)  # Normalizes the path
        '/fake_root/subdir2/file'
"""

import os
from typing import List, Optional

UNSET = None
RELATIVE = "rel"
ABSOLUTE = "abs"
REL = RELATIVE
ABS = ABSOLUTE


class PathAnchor:
    """A class representing a path with an optional parent point and display mode.

    This class handles path operations with support for anchored paths, allowing paths
    to be relative to a specified parent point. It also supports different display modes
    (absolute or relative paths).

    Attributes:
        path_anchor: The parent point for relative paths
        path_dir: The directory path
        path_mode: The display mode ('abs' or 'rel')
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        path: Optional[str] = None,
        mode: Optional[str] = None,
        parent: Optional["PathAnchor"] = None,
        clean: Optional[bool] = False,
        name: Optional[str] = None,
    ):
        """Initialize a PathAnchor object.

        Args:
            path (str): The path to use
            mode (Optional[str], optional): Display mode for path rendering.
                Can be 'abs' for absolute paths or 'rel' for relative paths.
                If None, the mode remains unchanged. Defaults to None.
            parent (Optional[PathAnchor], optional): Another PathAnchor object to use as
                reference point.
                Defaults to None.
            clean (Optional[bool], optional): If True, normalizes the path by resolving
                '..' and '.' components. Defaults to False.
            name (Optional[str], optional): The name of the anchor. String helper to
                identify the anchor for other uses. Defaults to None.
        """
        if path is None:
            raise RuntimeError("Path is required to create a PathAnchor")
        self.path_source = path
        self.parent = parent
        self.mode = mode
        self.clean = clean
        self.name = name

    def __repr__(self) -> str:
        """Return a string representation of the PathAnchor object.

        Returns:
            str: A string representation showing the path, parent (if present), and mode (if set)
        """
        name = self.name or self.__class__.__name__
        ret = f"<{name} {self.get_path()}"

        # Change if anchored
        parent = self.parent
        if parent:
            top_dir = parent.get_dir(clean=True)
            child_path = self.get_path(mode="rel", start=top_dir, clean=True)
            ret = f"<{name} [{top_dir}]{child_path}"

        # Add suffix
        suffix = ">"
        if self.mode:
            suffix = f" (mode={self.mode})>"
        return ret + suffix

    def __invert__(self) -> str:
        """Return the path as a string.

        Returns:
            str: The path as a string
        """
        return str(self.get_path())

    def __neg__(self) -> str:
        """Return the relative path as a string.

        Returns:
            str: The path as a string
        """
        return str(self.get_path(mode="rel"))

    def __pos__(self) -> str:
        """Return the absolute path as a string.

        Returns:
            str: The path as a string
        """
        return str(self.get_path(mode="abs"))

    def __call__(self, **kwargs) -> str:
        """Return the path as a string, accept get_path arguments.

        Returns:
            str: The path as a string
        """
        return str(self.get_path(**kwargs))

    def __truediv__(self, other):
        """Return a new PathAnchor with the other as path and self as left part."""
        return os.path.join(~self, str(other))

    def __rtruediv__(self, other):
        """Return a new PathAnchor with the other as path and self as rigth part."""
        return os.path.join(str(other), self.get_path(mode="rel"))

    def get_mode(self, lvl: int = 0) -> Optional[str]:
        """Get the effective display mode for this path.

        If this object has no mode set but has an parent, it will recursively
        check the parent's mode.

        Args:
            lvl (int, optional): Current recursion level. Defaults to 0.

        Returns:
            Optional[str]: The effective mode ('abs' or 'rel') or None if no mode is set
        """
        if isinstance(self.mode, str):
            return self.mode

        if self.parent:
            lvl += 1
            return self.parent.get_mode(lvl=lvl)
        return None

    def get_parents(self, itself: bool = False) -> List:
        """Get a list of all parent anchors in the parent chain.

        Args:
            itself (bool, optional): Include the current object in the result if True.
                Defaults to False.

        Returns:
            list[PathAnchor]: List of parent PathAnchor objects, ordered from current to root
        """
        ret = []
        ret.append(self)

        if self.parent:
            tmp = self.parent.get_parents(itself=True)
            ret.extend(tmp)

        if not itself:
            ret = ret[1:]
        return ret

    def get_dir(
        self,
        mode: Optional[str] = None,
        clean: Optional[bool] = None,
        start: Optional[str] = None,
        parent: Optional["PathAnchor"] = None,
    ) -> str:
        """Get the directory path according to specified parameters.

        Args:
            mode (Optional[str], optional): Output path format.
                Can be 'abs' for absolute path or 'rel' for relative path.
                If None, uses the object's mode setting. Defaults to None.
            clean (Optional[bool], optional): If True, normalizes the path by resolving
                '..' and '.' components. Defaults to False.
            start (Optional[str], optional): Base directory for relative path calculation
                when mode is 'rel'. Defaults to current working directory.
            parent (Optional[PathAnchor], optional): Override the parent point for this
                operation. Defaults to None.

        Returns:
            str: The processed directory path

        Raises:
            AssertionError: If an invalid mode is specified
        """
        ret = None
        mode = mode or self.get_mode()
        if not start:
            start = os.getcwd()
        clean = clean if isinstance(clean, bool) else self.clean

        # Resolve name
        if os.path.isabs(self.path_source):
            ret = self.path_source
        else:
            parent = parent or self.parent
            if parent:
                ret = os.path.join(parent.get_path(), self.path_source)
            else:
                ret = self.path_source

        # Clean
        if clean:
            ret = os.path.normpath(ret)

        # Ensure output format
        if mode == REL:
            if os.path.isabs(ret):
                ret = os.path.relpath(ret, start=start)
        elif mode == ABS:
            if not os.path.isabs(ret):
                ret = os.path.abspath(ret)
        elif mode is UNSET:
            pass
        else:
            raise ValueError(f"Invalid mode: {mode}")

        return ret

    def get_path(self, **kwargs) -> str:
        """Get the path using the same parameters as get_dir.

        Returns:
            str: The processed path
        """
        return self.get_dir(**kwargs)

    def get_name(self) -> str:
        """Get the basename of the anchor.

        Returns:
            str: The name of the anchor
        """
        return os.path.basename(self.get_path(mode="abs"))


class FileAnchor(PathAnchor):
    """A class representing a file path with optional parent point and display mode.

    This class extends PathAnchor to handle file paths specifically, maintaining
    separate tracking of directory and filename components.

    Attributes:
        path_dir: The directory component of the path
        path_file: The filename component of the path
        path_anchor: The parent point for relative paths
        path_mode: The display mode ('abs' or 'rel')
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        path: Optional[str] = None,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        mode: Optional[str] = None,
        parent: Optional["PathAnchor"] = None,
        name: Optional[str] = None,
    ):
        """Initialize a FileAnchor object.

        The path can be specified either as a full path or as separate directory
        and file components.

        Args:
            path (str): The complete file path
            directory (Optional[str], optional): The directory component. If provided with filename,
                path parameter is ignored. Defaults to None.
            filename (Optional[str], optional): The filename component. Defaults to None.
            mode (Optional[str], optional): Display mode for path rendering.
                Can be 'abs' for absolute paths or 'rel' for relative paths.
                If None, the mode remains unchanged. Defaults to None.
            parent (Optional[PathAnchor], optional): Another PathAnchor object to use
                as reference point. Defaults to None.

        Raises:
            AssertionError: If the provided path components don't match the expected format
        """
        if filename and directory and path:
            raise RuntimeError("filename, directory and path cannot be provided")

        if filename and os.path.sep in filename:
            raise RuntimeError(
                f"filename cannot contain path separators, got: {filename}"
            )

        if filename and directory:
            # Ignore path
            path = os.path.join(directory, filename)
        elif filename and path:
            path = os.path.join(path, filename)
            directory = path
        elif path and directory:
            assert path.startswith(directory)
            filename = path[len(directory) :]
        elif filename:
            path = filename
            if parent:
                directory = parent.get_path()
                if directory and directory != ".":
                    path = os.path.join(directory, filename)
        elif path:
            directory, filename = os.path.split(path)

        assert path == os.path.join(
            directory, filename
        ), f"Got: {path} == {os.path.join(directory, filename)}"

        super().__init__(path=directory, mode=mode, name=name, parent=parent)
        self.filename_source = path
        self.filename = filename

    def get_path(self, **kwargs) -> str:
        """Get the complete file path.

        This method combines the directory path from get_dir() with the filename.
        All kwargs are passed to get_dir().

        Returns:
            str: The complete file path (directory + filename)
        """
        dir_path = self.get_dir(**kwargs)
        file_name = self.filename
        if not dir_path or dir_path == ".":
            return file_name
        return os.path.join(dir_path, file_name)
