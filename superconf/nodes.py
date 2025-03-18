"""Configuration node classes for managing hierarchical configuration.

This module provides the core Node class and related functionality for managing
hierarchical configuration data. The Node class serves as the base class for all
configuration objects in the superconf library.

Key features:
- Hierarchical configuration with parent-child relationships
- Flexible value querying with multiple fallback levels
- Support for metadata and configuration overrides
- Type checking and validation
- Customizable behavior through Meta class settings

The Node class implements a sophisticated configuration query system that checks
multiple sources in a defined precedence order:

1. Dictionary overrides
2. Instance attributes with _name prefix 
3. Class Meta attributes
4. Instance attributes with meta__ prefix
5. Parent configuration objects

This allows for flexible configuration management while maintaining strict type
safety and validation.
"""

import copy
import logging
from pprint import pprint
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

from superconf import exceptions
from superconf.common import NOT_SET, UNSET_ARG

logger = logging.getLogger(__name__)

T = TypeVar("T", bound="Node")


class BaseNode:
    """Base class for configuration objects providing core configuration query functionality.

    This class implements hierarchical configuration management with support for querying values
    from multiple sources in a defined precedence order:
    1. Dictionary overrides
    2. Instance attributes with _name prefix
    3. Class Meta attributes
    4. Instance attributes with meta__ prefix
    5. Parent configuration objects

    Attributes:
        __key__: Configuration key identifier
        __parent__: Reference to parent configuration object
        __value__: Stored configuration value
        Meta: Inner class for class-level configuration settings
    """

    __key__: Optional[Union[str, int]] = None
    __parent__: Optional["Node"] = None
    __value__: Any = NOT_SET

    class Meta:
        """Class to store class-level configuration settings."""

    def __init__(
        self,
        key: Optional[Union[str, int]] = None,
        value: Any = NOT_SET,
        parent: Optional["Node"] = None,
    ) -> None:
        """Initialize a configuration node.

        Args:
            key: The configuration key identifier
            value: The configuration value
            parent: Parent configuration object if this is a child config
        """
        self.__key__ = key
        self.__parent__ = parent
        self.__value__ = value

    @property
    def key(self) -> Optional[Union[str, int]]:
        """The configuration key identifier."""
        return self.__key__ or None

    @key.setter
    def key(self, value: Optional[Union[str, int]]):
        self.__key__ = value

    @property
    def parent(self) -> Optional["Node"]:
        """The parent configuration object."""
        return self.__parent__

    @parent.setter
    def parent(self, value: Optional["Node"]):
        self.__parent__ = value

    @property
    def name(self) -> str:
        """The display name - either the key or class name."""
        if self.__key__ is not None:
            return str(self.__key__)
        return self.__class__.__name__

    @property
    def fname(self) -> str:
        """The full hierarchical name including all parent names."""
        curr = self
        out = []
        while curr is not None:
            # print("WIPPP", curr, type(curr.name), curr.name)
            name = curr.name
            assert isinstance(
                name, str
            ), f"Object {curr} does not have a valid name, got: {name}"
            out.append(name)
            curr = curr.parent
        out.reverse()
        return ".".join(out)

    @property
    def fkey(self) -> str:
        """The full hierarchical key including all parent keys."""
        curr = self
        out = []
        while curr is not None:
            curr_key = curr.key
            if not isinstance(curr_key, (int, str)):
                curr_key = ""
            out.append(curr_key)
            curr = curr.parent
        out.reverse()
        return ".".join(out)


class Node(BaseNode):
    "Node with config management and inheritance"

    # Instance config management
    # ----------------------------

    def get_hierarchy(self) -> List["Node"]:
        """Return the configuration hierarchy from self to root.

        Returns:
            List of Node objects representing the configuration hierarchy,
            starting with self and ending with the root node.
        """
        out = [self]

        target = self
        while target.__parent__ is not None and target.__parent__ not in out:
            target = target.__parent__
            out.append(target)

        return out

    def query_inst_cfg(
        self,
        name: str,
        cast: Optional[Type] = None,
        report: Optional[List] = None,
        **kwargs,
    ) -> Any:
        """Query instance configuration with optional type casting.

        Args:
            name: Configuration setting name to query
            cast: Optional type to cast the result to
            report: Optional list to collect query trace information
            **kwargs: Additional arguments passed to _query_inst_cfg

        Returns:
            The configuration value, optionally cast to the specified type

        Raises:
            AssertionError: If casting fails
        """
        report = report if isinstance(report, list) else []
        out = self._query_inst_cfg(name, report=report, **kwargs)
        logger.debug("Node config query for %s.%s=%s", self, name, out)

        if isinstance(out, (dict, list)):
            out = copy.copy(out)

        if cast is not None:
            # Try to cast if asked
            if not out:
                out = cast()
            assert isinstance(
                out, cast
            ), f"Wrong type for config {self}, expected {cast}, got: {type(out)} {out}"
        return out

    def _query_inst_cfg(
        self,
        name: str,
        override: Optional[Dict] = None,
        default: Any = UNSET_ARG,
        report: Optional[List] = None,
    ) -> Any:
        """Internal method to query instance configuration from various sources.

        Searches for configuration values in the following precedence order:
        1. Dictionary override if provided
        2. Instance attribute with _name prefix
        3. Class Meta attribute via __meta__
        4. Class Meta attribute via Meta class
        5. Instance attribute with meta__ prefix
        6. Default value if provided

        Args:
            name: Configuration setting name to query
            override: Optional dictionary of override values
            default: Default value if setting is not found
            report: Optional list to collect query trace information

        Returns:
            The configuration value if found

        Raises:
            UnknownSetting: If the setting is not found and no default is provided
        """
        query_from = report if isinstance(report, list) else []

        # Fetch from dict override, if provided
        if isinstance(override, dict):
            val = override.get(name, UNSET_ARG)
            if val is not UNSET_ARG:
                query_from.append(f"dict_override:{name}")
                return val
        elif override is not None:
            raise ValueError(f"Invalid override type: {type(override)}")

        # Fetch from self._NAME
        # Good for initial setup, if write mode is required
        val = getattr(self, f"_{name}", UNSET_ARG)
        if val is not UNSET_ARG:
            query_from.append(f"self_attr:_{name}")
            return val

        # Fetch from self.__meta__.NAME
        cls = self
        if hasattr(cls, "__meta__"):
            val = getattr(cls.__meta__, name, UNSET_ARG)
            if val != UNSET_ARG:
                query_from.append(f"class_meta:__meta__.{name}")
                return val

        # Python class params: self.Meta.NAME
        # Good for class overrides
        cls = self
        if hasattr(cls, "Meta"):
            val = getattr(cls.Meta, name, UNSET_ARG)
            if val != UNSET_ARG:
                query_from.append(f"class_meta:Meta.{name}")
                return val

        # Fetch from self.meta__NAME
        # Python class inherited params (good for defaults)
        val = getattr(self, f"meta__{name}", UNSET_ARG)
        if val is not UNSET_ARG:
            query_from.append(f"self_attr:meta__{name}")
            return val

        if default is not UNSET_ARG:
            query_from.append("default_arg")
            return default

        msg = (
            f"Setting '{name}' has not been declared before being used"
            f" in '{repr(self)}', please declare 'meta__{name}' attribute, tried to query: {query_from}"
        )
        raise exceptions.UnknownSetting(msg)

    # TODO: Deprecate query_inst_cfg, and use this method instead
    # Add support for folowing parameters
    def query_cfg(
        self,
        name: str,
        include_self: bool = True,
        include_parents: bool = True,
        include_root: bool = True,
        report: bool = False,
        **kwargs,
    ) -> Any:
        """Query configuration from self and parent hierarchy.

        Args:
            name: Configuration setting name to query
            include_self: Whether to include self in the query
            report: Whether to return query trace information
            **kwargs: Additional arguments passed to query_parent_cfg

        Returns:
            The configuration value, optionally with query trace information
        """
        return self.query_parent_cfg(
            name, include_self=include_self, report=report, **kwargs
        )

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def query_parent_cfg(
        self,
        name: str,
        as_subkey: bool = False,
        cast: Optional[Type] = None,
        default: Any = UNSET_ARG,
        include_self: bool = False,
        report: bool = False,
    ) -> Any:
        """Query configuration from parent hierarchy.

        Args:
            name: Configuration setting name to query
            as_subkey: If True and parent value is dict/list, get value using self.__key__
            cast: Optional type to cast the result to
            default: Default value if setting is not found
            include_self: Whether to include self in the query
            report: Whether to return query trace information

        Returns:
            The configuration value, optionally with query trace information

        Raises:
            UnknownSetting: If setting is not found and no default provided
            AssertionError: If casting fails or invalid key type for list access
        """

        # Fast exit or raise exception
        if not self.__parent__ and include_self is False:
            if default is not UNSET_ARG:
                if report:
                    return default, "No parents, return default value"
                return default
            msg = (
                f"Setting '{name}' has not been declared in hierarchy of '{repr(self)}'"
            )
            raise exceptions.UnknownSetting(msg)

        # Check parents
        _report = []
        parents = self.get_hierarchy()
        if include_self is False:
            parents = parents[1:]
        out = NOT_SET
        for parent in parents:
            _report.append(f"Check '{name}' in parent {parent}")

            if report:
                out, _report2 = parent.query_inst_cfg(
                    name, default=NOT_SET, report=True
                )
                _report.append(_report2)
            else:
                out = parent.query_inst_cfg(name, default=NOT_SET)

            # If a value is found, then scan it
            if out is not NOT_SET:
                _report.append(f"Found '{name}' in parent {parent}= {out}")

                # Ckeck subkey
                if as_subkey is True:
                    if isinstance(out, dict):
                        out = out.get(self.__key__, NOT_SET)
                    elif isinstance(out, list):
                        assert isinstance(self.__key__, int), f"Got: {self.__key__}"
                        out = out[self.__key__]
                    else:
                        out = NOT_SET
                _report.append(f"Found2 '{name}' in parent {parent}= {out}")

            # Don't ask more parents if value is found
            if out is not NOT_SET:
                break

        if out is NOT_SET:
            _report.append(f"NotFound '{name}' in parent: {parent}")

        if cast is not None:
            # Try to cast if asked
            if not out:
                out = cast()
            assert isinstance(
                out, cast
            ), f"Wrong type for config {name}, expected {cast}, got: {type(out)} {out}"

        if out is NOT_SET and default is UNSET_ARG:
            msg = (
                f"Setting '{name}' has not been declared in hierarchy of '{repr(self)}'"
            )
            raise exceptions.UnknownSetting(msg)

        if report:
            return out, _report
        return out
