"""Path anchoring and manipulation library for flexible path resolution.

This module provides classes for handling paths with anchor points, allowing for flexible
path resolution relative to different base directories. It's particularly useful for
configuration management and file organization where paths need to be resolved relative
to different root directories.

Main Components:
    - PathAnchor: Base class for handling directory paths with anchor points
    - FileAnchor: Extension of PathAnchor for handling file paths specifically

Key Features:
    - Path resolution relative to anchor points
    - Support for both absolute and relative path modes
    - Chain of anchor points for complex path hierarchies
    - Clean path normalization
    - Flexible path representation

Examples:
    Basic path anchoring:

    >>> project_dir = "/fake/prj"
    >>> root = PathAnchor(project_dir)
    >>> conf = PathAnchor("../../common_conf", anchor=root, mode="abs")
    >>> inventory = PathAnchor("inventory/", anchor=conf, mode="rel")
    >>> 
    >>> # Get paths in different modes
    >>> conf.get_dir()  # Returns absolute path
    '/fake/common_conf'
    >>> inventory.get_dir()  # Returns relative path
    '../../inventory'

    File handling:

        >>> root = PathAnchor("/fake/prj")
        >>> config_file = FileAnchor("subconf/myfile.yml", anchor=root)
        >>> config_file.get_path()  # Full path
        '/fake/prj/subconf/myfile.yml'
        >>> config_file.get_file()  # Just filename
        'myfile.yml'
        >>> config_file.get_dir()   # Just directory
        '/fake/prj/subconf'

    Complex path resolution:

        >>> project = PathAnchor("/fake_root/project")
        >>> path = PathAnchor("subdir2/../../subdir2/file", anchor=project)
        >>> path.get_dir(clean=True)  # Normalizes the path
        '/fake_root/subdir2/file'
"""

import os

# from pprint import pprint
from typing import List, Optional


class PathAnchor:
    """A class representing a path with an optional anchor point and display mode.

    This class handles path operations with support for anchored paths, allowing paths
    to be relative to a specified anchor point. It also supports different display modes
    (absolute or relative paths).

    Attributes:
        path_anchor: The anchor point for relative paths
        path_dir: The directory path
        path_mode: The display mode ('abs' or 'rel')
    """

    def __init__(
        self,
        path: str,
        mode: Optional[str] = None,
        anchor: Optional["PathAnchor"] = None,
    ):
        """Initialize a PathAnchor object.

        Args:
            path (str): The path to use
            mode (Optional[str], optional): Display mode for path rendering.
                Can be 'abs' for absolute paths or 'rel' for relative paths.
                If None, the mode remains unchanged. Defaults to None.
            anchor (Optional[PathAnchor], optional): Another PathAnchor object to use as
                reference point.
                Defaults to None.
        """
        self.path_anchor = anchor
        self.path_dir = path
        self.path_mode = mode

    def __repr__(self) -> str:
        """Return a string representation of the PathAnchor object.

        Returns:
            str: A string representation showing the path, anchor (if present), and mode (if set)
        """
        name = self.__class__.__name__
        ret = f"<{name} {self.get_path()}"

        # Change if anchored
        anchor = self.path_anchor
        if anchor:
            ret = f"<{name} [{anchor.get_dir()}]{self.get_path()}"

        # Add suffix
        suffix = ">"
        if self.path_mode:
            suffix = f" (mode={self.path_mode})>"
        return ret + suffix

    def get_mode(self, lvl: int = 0) -> Optional[str]:
        """Get the effective display mode for this path.

        If this object has no mode set but has an anchor, it will recursively
        check the anchor's mode.

        Args:
            lvl (int, optional): Current recursion level. Defaults to 0.

        Returns:
            Optional[str]: The effective mode ('abs' or 'rel') or None if no mode is set
        """
        if isinstance(self.path_mode, str):
            return self.path_mode

        if self.path_anchor:
            lvl += 1
            return self.path_anchor.get_mode(lvl=lvl)
        return None

    def get_parents(self, itself: bool = False) -> List:
        """Get a list of all parent anchors in the anchor chain.

        Args:
            itself (bool, optional): Include the current object in the result if True.
                Defaults to False.

        Returns:
            list[PathAnchor]: List of parent PathAnchor objects, ordered from current to root
        """
        ret = []
        ret.append(self)

        if self.path_anchor:
            tmp = self.path_anchor.get_parents(itself=True)
            ret.extend(tmp)

        if not itself:
            ret = ret[1:]
        return ret

    def get_dir(
        self,
        mode: Optional[str] = None,
        clean: Optional[bool] = False,
        start: Optional[str] = None,
        anchor: Optional["PathAnchor"] = None,
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
            anchor (Optional[PathAnchor], optional): Override the anchor point for this
                operation. Defaults to None.

        Returns:
            str: The processed directory path

        Raises:
            AssertionError: If an invalid mode is specified
        """
        ret = None
        mode = mode or self.get_mode()
        start = start or os.getcwd()

        # Resolve name
        if os.path.isabs(self.path_dir):
            ret = self.path_dir
        else:
            anchor = anchor or self.path_anchor
            if anchor:
                ret = os.path.join(anchor.path_dir, self.path_dir)
            else:
                ret = self.path_dir

        # Clean
        if clean:
            ret = os.path.normpath(ret)

        # Ensure output format
        if mode == "rel":
            if os.path.isabs(ret):
                ret = os.path.relpath(ret, start=start)
        elif mode == "abs":
            if not os.path.isabs(ret):
                ret = os.path.abspath(ret)
        elif mode is None:
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


class FileAnchor(PathAnchor):
    """A class representing a file path with optional anchor point and display mode.

    This class extends PathAnchor to handle file paths specifically, maintaining
    separate tracking of directory and filename components.

    Attributes:
        path_dir: The directory component of the path
        path_file: The filename component of the path
        path_anchor: The anchor point for relative paths
        path_mode: The display mode ('abs' or 'rel')
    """

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def __init__(
        self,
        path: str,
        directory: Optional[str] = None,
        filename: Optional[str] = None,
        mode: Optional[str] = None,
        anchor: Optional["PathAnchor"] = None,
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
            anchor (Optional[PathAnchor], optional): Another PathAnchor object to use
                as reference point. Defaults to None.

        Raises:
            AssertionError: If the provided path components don't match the expected format
        """
        if directory and filename:
            # Ignore path
            path = os.path.join(directory, filename)
        elif path and filename:
            path = os.path.join(path, filename)
            directory = path
        elif path and directory:
            assert path.startswith(directory)
            filename = path[len(directory) :]
        elif path:
            directory, filename = os.path.split(path)

        assert path == os.path.join(
            directory, filename
        ), f"Got: {path} == {os.path.join(directory, filename)}"

        super().__init__(directory, mode=mode, anchor=anchor)
        self.path_file = filename

    def get_path(self, **kwargs) -> str:
        """Get the complete file path.

        This method combines the directory path from get_dir() with the filename.
        All kwargs are passed to get_dir().

        Returns:
            str: The complete file path (directory + filename)
        """
        return os.path.join(self.get_dir(**kwargs), self.get_file())

    def get_file(self) -> str:
        """Get the filename component of the path.

        Returns:
            str: The filename without directory path
        """
        return self.path_file
