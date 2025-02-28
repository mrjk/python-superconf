
import logging
import copy
from pprint import pprint

from superconf.common import NOT_SET, UNSET_ARG

from superconf import exceptions


logger = logging.getLogger(__name__)



class Node:
    """Base class for configuration objects providing core configuration query functionality.

    This class implements the basic configuration query mechanisms used by all configuration
    classes. It supports querying configuration values from various sources including
    instance attributes, class Meta attributes, and parent configurations.
    """

    __key__ = None
    __parent__ = None
    __value__ = NOT_SET

    class Meta:
        """Class to store class-level configuration overrides."""

    def __init__(self, key=None, value=NOT_SET, parent=None):
        """Initialize a configuration base instance.

        Args:
            key: The configuration key name
            value: The configuration value (defaults to NOT_SET)
            parent: Parent configuration object if this is a child config
        """
        self.__key__ = key
        self.__parent__ = parent
        self.__value__ = value


    @property
    def key(self):
        "Key"
        return self.__key__ or None

    @property
    def parent(self):
        "Parent"
        return self.__parent__
    

    @property
    def name(self):
        "Name"
        return self.key or self.__class__.__name__


    @property
    def fname(self):
        "Full name"
        curr = self
        out = []
        while curr is not None:
            out.append(curr.name)
            curr = curr.parent
        out.reverse()
        return ".".join(out)

    @property
    def fkey(self):
        "Full key"
        curr = self
        out = []
        while curr is not None:
            curr_key = curr.key
            if not isinstance(curr_key, (int, str)):
                curr_key = ""
                # break
            out.append(curr_key)
            curr = curr.parent
        out.reverse()
        return ".".join(out)


    # Instance config management
    # ----------------------------

    def query_inst_cfg(self,name, cast=None, report=None, **kwargs):
        """Query instance configuration with optional type casting.

        Args:
            *args: Variable length argument list passed to _query_inst_cfg
            cast: Optional type to cast the result to
            **kwargs: Arbitrary keyword arguments passed to _query_inst_cfg

        Returns:
            The configuration value, optionally cast to the specified type
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

    def _query_inst_cfg(self, name, override=None, default=UNSET_ARG, report=None):
        """Internal method to query instance configuration from various sources.

        Searches for configuration values in the following order:
        1. Dictionary override if provided
        2. Instance attribute with _name prefix
        3. Class Meta attribute
        4. Instance attribute with meta__ prefix
        5. Default value if provided

        Args:
            name: Configuration setting name to query
            override: Optional dictionary of override values
            parents: Whether to check parent configurations
            default: Default value if setting is not found

        Returns:
            Tuple of (value, query_sources) where query_sources is a list of searched locations

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
            # print("Meta Value", cls.__meta__, name, val)
            # pprint(cls.__meta__)
            # pprint(cls.__meta__.__dict__)
            if val != UNSET_ARG:
                query_from.append(f"class_meta:__meta__.{name}")
                # print ("SELF CLASS Meta retrieval for: {cls}" , name, val)
                return val

        # Python class params: self.Meta.NAME
        # Good for class overrides
        cls = self
        if hasattr(cls, "Meta"):
            val = getattr(cls.Meta, name, UNSET_ARG)
            # print("Meta Value", cls.Meta, name, val)
            # pprint(cls.__meta__)
            # pprint(cls.__meta__.__dict__)
            if val != UNSET_ARG:
                query_from.append(f"class_meta:Meta.{name}")
                # print ("SELF CLASS Meta retrieval for: {cls}" , name, val)
                return val


        # Fetch from self.meta__NAME
        # Python class inherited params (good for defaults)
        val = getattr(self, f"meta__{name}", UNSET_ARG)
        if val is not UNSET_ARG:
            query_from.append(f"self_attr:meta__{name}")
            return val

        if default is not UNSET_ARG:
            query_from.append("default_arg")
            return default, query_from

        msg = (
            f"Setting '{name}' has not been declared before being used"
            f" in '{repr(self)}', please declare 'meta__{name}' attribute, tried to query: {query_from}"
        )
        raise exceptions.UnknownSetting(msg)

    def query_cfg(self, name, include_self=True, report=False, **kwargs):
        "Temporary wrapper"
        return self.query_parent_cfg(name, include_self=True, report=report, **kwargs)

    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def query_parent_cfg(
        self,
        name,
        as_subkey=False,
        cast=None,
        default=UNSET_ARG,
        include_self=False,
        report=False,
    ):
        """Query configuration from parent object.

        Args:
            name: Configuration setting name to query
            as_subkey: If True and parent value is dict, get self.__key__ from it
            cast: Optional type to cast the result to
            default: Default value if setting is not found

        Returns:
            The configuration value from the parent, optionally cast to specified type

        Raises:
            UnknownSetting: If no parent exists and no default is provided
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

    def get_hierarchy(self):
        "Return a list of parents NEW VERSION"
        out = [self]

        target = self
        while target.__parent__ is not None and target.__parent__ not in out:
            target = target.__parent__
            out.append(target)

        return out
