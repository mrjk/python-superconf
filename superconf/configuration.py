"Main configuratio  class"


# pylint: disable=unused-argument, too-few-public-methods, too-many-instance-attributes, use-dict-literal

import copy
import logging
from collections import OrderedDict

# from collections import Mapping, Sequence
from collections.abc import Mapping, Sequence

from superconf import exceptions

from .common import NOT_SET, UNSET_ARG
from .fields import Field, FieldConf
from .loaders import Environment

# from pprint import pprint


# from types import SimpleNamespace
# from typing import Callable


logger = logging.getLogger(__name__)


# ====================================
# Configuration Child
# ====================================


class _ConfigurationBase:
    """Base class for configuration objects providing core configuration query functionality.

    This class implements the basic configuration query mechanisms used by all configuration
    classes. It supports querying configuration values from various sources including
    instance attributes, class Meta attributes, and parent configurations.
    """

    class Meta:
        """Class to store class-level configuration overrides."""

    def __init__(self, key=None, value=NOT_SET, parent=None):
        """Initialize a configuration base instance.

        Args:
            key: The configuration key name
            value: The configuration value (defaults to NOT_SET)
            parent: Parent configuration object if this is a child config
        """
        self.key = key
        self._parent = parent
        self._value = value
        self._cache = True  # TOFIX

    # Instance config management
    # ----------------------------

    def query_inst_cfg(self, *args, cast=None, **kwargs):
        """Query instance configuration with optional type casting.

        Args:
            *args: Variable length argument list passed to _query_inst_cfg
            cast: Optional type to cast the result to
            **kwargs: Arbitrary keyword arguments passed to _query_inst_cfg

        Returns:
            The configuration value, optionally cast to the specified type
        """
        out, _ = self._query_inst_cfg(*args, **kwargs)
        # print(f"CONFIG QUERY FOR {self}: {args[0]} {query_from} => {out}")
        # pprint(query_from)

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

    # @classmethod
    # def _query_cls_cfg(cls, *args, **kwargs):
    #     "Temporary class method"
    #     out = cls._query_inst_cfg(cls, *args, **kwargs)
    #     if isinstance(out, (dict, list)):
    #         out = copy.copy(out)
    #     return out

    def _query_inst_cfg(self, name, override=None, default=UNSET_ARG):
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
        query_from = []

        # Fetch from dict override, if provided
        if isinstance(override, dict):
            val = override.get(name, NOT_SET)
            if val is not NOT_SET:
                query_from.append(f"dict_override:{name}")
                return val, query_from

        # Fetch from self._NAME
        # Good for initial setup, if write mode is required
        val = getattr(self, f"_{name}", NOT_SET)
        if val is not NOT_SET:
            query_from.append(f"self_attr:_{name}")
            return val, query_from

        # Python class params
        # Good for class overrides
        cls = self
        if hasattr(cls, "Meta"):
            val = getattr(cls.Meta, name, NOT_SET)
            if val is not NOT_SET:
                query_from.append(f"self_meta:Meta.{name}")
                # print ("SELF CLASS Meta retrieval for: {cls}" , name, val)
                return val, query_from

        # Fetch from self.meta__NAME
        # Python class inherited params (good for defaults)
        val = getattr(self, f"meta__{name}", NOT_SET)
        if val is not NOT_SET:
            query_from.append(f"self_attr:meta__{name}")
            return val, query_from

        if default is not UNSET_ARG:
            query_from.append("default_arg")
            return default, query_from

        msg = (
            f"Setting '{name}' has not been declared before being used"
            f" in '{repr(self)}', tried to query: {query_from}"
        )
        raise exceptions.UnknownSetting(msg)

    def query_parent_cfg(self, name, as_subkey=False, cast=None, default=UNSET_ARG):
        """Query configuration from parent object.

        Args:
            name: Configuration setting name to query
            as_subkey: If True and parent value is dict, get self.key from it
            cast: Optional type to cast the result to
            default: Default value if setting is not found

        Returns:
            The configuration value from the parent, optionally cast to specified type

        Raises:
            UnknownSetting: If no parent exists and no default is provided
        """
        # Fast exit or raise exception
        if not self._parent:
            if default is not UNSET_ARG:
                return default
            msg = (
                f"Setting '{name}' has not been declared in hierarchy of '{repr(self)}'"
            )
            raise exceptions.UnknownSetting(msg)

        def fetch_closest_parent(name):
            # Fetch from closest parent
            val = self._parent.query_inst_cfg(name, default=NOT_SET)
            if val is NOT_SET:
                return val

            # TOFIX; Only works for dicts ?
            if as_subkey is True and isinstance(val, dict):
                val = val.get(self.key, NOT_SET)

            return val

        func_list = [
            fetch_closest_parent,
        ]

        # Loop over functions
        out = NOT_SET
        for func in func_list:
            out = func(name)
            if out is not NOT_SET:
                break

        if cast is not None:
            # Try to cast if asked
            if not out:
                out = cast()
            assert isinstance(
                out, cast
            ), f"Wrong type for config {name}, expected {cast}, got: {type(out)} {out}"
        return out


# ====================================
# Configuration Container
# ====================================


class _Configuration(_ConfigurationBase):
    """Base configuration container class that manages configuration fields and values.

    This class extends _ConfigurationBase to provide field management, value caching,
    and dynamic child configuration creation capabilities.
    """

    _declared_values = {}

    def __init__(self, *, key=None, value=NOT_SET, parent=None, meta=None, **kwargs):
        """Initialize a configuration container.

        Args:
            key: Configuration key name
            value: Initial configuration value
            parent: Parent configuration object
            meta: Optional meta configuration
            **kwargs: Additional configuration options
        """

        # super(_Configuration, self).__init__(key=key, value=value, parent=parent)
        super().__init__(key=key, value=value, parent=parent)

        # As this can be updated during runtime ...
        # self._declared_values = self._declared_values
        # self._declared_values = dict()
        self._cached_values = {}

        kwargs.update(
            dict(
                key=key,
                # loaders=loaders,
                # cache=cache,
                parent=parent,
            )
        )

        # self._loaders = NOT_SET
        self._loaders = self.query_inst_cfg("loaders", override=kwargs)
        # self._cache = self.query_inst_cfg("cache", override=kwargs)
        self._cache = True  # TOFIX

        self._extra_fields_enabled = self.query_inst_cfg(
            "extra_fields",
            override=kwargs,
            default=True,  # TOFIX, should be set to false by default
        )
        self._extra_fields = {}
        self._children_class = self.query_inst_cfg(
            "children_class", override=kwargs, default=NOT_SET
        )

        self._cast = self.query_inst_cfg("cast", override=kwargs, default=None)
        self._strict_cast = self.query_inst_cfg("strict_cast", override=kwargs)

        self._default = self.query_inst_cfg("default", override=kwargs, default=NOT_SET)
        if self._default is NOT_SET:
            self._default = self.query_parent_cfg(
                "default", as_subkey=True, default=NOT_SET
            )

        # print ("\n\n===== CREATE NEW CONFIG", self.key, self, value)
        # child_values = value
        child_values = self._value
        if child_values is NOT_SET:
            # print(f"REMAP CHILD VALUE {self}:{key}: {child_values}=>{self._default}")
            child_values = self._default
        self.set_dyn_children(child_values)
        self.set_values(child_values)

    def set_dyn_children(self, value):
        "Placeholder"

    # Generic API
    # ----------------------------

    # Field compat API
    @property
    def default(self):
        "Temporary property to access to self._default"
        return self._default

    @property
    def cast(self):
        "Temporary property to access to self._default"
        return self._cast

    # Field compatibility layer !
    # This basically respect default python behavior , when this is a children...
    def __get__(self, conf_instance, owner):
        # if conf_instance:
        #     return conf_instance.get_field_value(field=self)
        return self

    def __getitem__(self, value):
        return self.declared_fields[value].__get__(self, self.__class__)

    # def __repr__(self):
    #     return "{}(loaders=[{}])".format(
    #         self.__class__.__name__,
    #         ", ".join([str(loader) for loader in self._loaders]),
    #     )

    # def __str__(self):
    #     values = []
    #     for _, v in self:
    #         if v.default is NOT_SET and not v.help:
    #             help = "No default value provided"
    #         elif not v.help:
    #             help = "Default value is {}.".format(repr(v.default))
    #         else:
    #             help = v.help
    #         try:
    #             values.append(
    #                 "{}={} - {}".format(v.key, repr(getattr(self, v.key)), help)
    #             )
    #         except UnknownConfiguration:
    #             values.append("{}=NOT_SET - {}".format(v.key, help))
    #     return "\n".join(values)

    # Value management
    # ----------------------------

    def get_value(self, key, lvl=-1, **kwargs):
        """Get configuration value for a given key.

        Args:
            key: Configuration key to retrieve
            lvl: Recursion level for nested configurations
            **kwargs: Additional arguments passed to get_field_value

        Returns:
            Configuration value for the specified key
        """
        assert isinstance(key, str)
        return self.get_field_value(key, **kwargs)

    def reset(self):
        """Reset all loaders and clear cached values.

        This should be called when configuration values need to be reloaded.
        """
        for loader in self._loaders:
            loader.reset()
        self._cached_values = {}

    def get_field_value(self, key=None, field=None, default=UNSET_ARG, **kwargs):
        """Get value for a configuration field.

        Args:
            key: Configuration key name
            field: Configuration field object
            default: Default value if not found
            **kwargs: Additional arguments for child creation

        Returns:
            Configuration value for the specified field

        Raises:
            UndeclaredField: If field is not found and no default provided
        """

        # Parse input
        if field is None and key is None:
            assert False, "BUG herrrrr"

        if field is None:
            assert isinstance(key, (str, int))

            field = self.declared_fields.get(key, None)
            if field is None:
                if default is not UNSET_ARG:
                    return default
                raise exceptions.UndeclaredField(f"Configuration '{key}' not found")
            assert key == field.key, f"Got: {key} != {field.key}"
            key = field.key

        if key is None:
            key = field.key

        # Check in cache
        if self._cache and key in self._cached_values:
            return self._cached_values[key]

        conf = self.create_child(key, field, **kwargs)
        assert isinstance(
            conf, (type(None), bool, int, str, Sequence, Mapping, ConfigurationDict)
        ), f"Got: {type(conf)}"

        if self._cache:
            self._cached_values[key] = conf
            # print("CACHE CHILD", self, key, conf)
        return conf

    def get_values(self, lvl=-1, **kwargs):
        "Return all values of the container"

        if lvl == 0:
            return self

        out = {}
        for key, _ in self.declared_fields.items():
            val = self.get_field_value(key)
            if isinstance(val, ConfigurationDict):
                val = val.get_values(lvl=lvl - 1)

            out[key] = val

        return out

    # This should be split if field has children or not ...
    def create_child(self, key, field, value=NOT_SET, **kwargs):
        """
        :param item:    Name of the setting to lookup.
        :param default: Default value if none is provided. If left unset,
                        loading a self that fails to provide this value
                        will raise a UnknownConfiguration exception.
        :param cast:    Callable to cast variable with. Defaults to type of
                        default (if provided), identity if default is not
                        provided or raises TypeError if provided cast is not
                        callable.
        :param loaders: A list of loader instances in the order they should be
                        looked into. Defaults to `[Environment()]`
        """

        # General lookup policy
        #  - kwargs default override
        #  - current object defaults
        #      - Must be a dict, and the key must be present or NEXT
        #  - child
        #      - DEfault must be set
        #  - UNSET

        # DElegate logic to field methods
        result, meta = field.resolve_value(
            self,
            value=value,
        )

        # TOFIX: To be migrated into FieldConf
        default = meta.default
        value = meta.value

        # print ("DUMP CHILD CREATE META", self, key)
        # pprint (meta.__dict__)

        # If not container, return HERE
        if not isinstance(field, FieldConf):
            return result

        # Default children_class
        children_class = field.children_class
        if children_class is NOT_SET:
            children_class = self._children_class
            # children_class = getattr(field, "children_class", NOT_SET)

        assert (
            children_class
        ), f"Got: {type(children_class)}: {children_class} for {self}:{key}"

        out = children_class(
            key=key, value=value, default=default, parent=self, **kwargs
        )

        return out

    @property
    def declared_fields(self):
        "Return declared fields"
        out = {}
        if self._extra_fields:
            # Add extra fields
            out.update(self._extra_fields)

        # Always use explicit fields
        out.update(self._declared_values)
        return out

    def set_values(self, value):
        "Set a value"

        # Instanciate containers fields - Automatic
        for key, field in self.declared_fields.items():

            if field.is_container():

                # Create child then
                val = NOT_SET
                if value and isinstance(value, Mapping):
                    try:
                        val = value.get(key, NOT_SET)
                    except AttributeError:
                        val = NOT_SET
                if value and isinstance(value, Sequence):
                    try:
                        val = value[key]
                    except IndexError:
                        val = NOT_SET

                # print ("AUTOMATIC CREATE CHILD CONTAINER", key, field, val)
                conf = self.create_child(key, field, value=val)
                assert isinstance(conf, (_Configuration)), f"Got: {type(conf)}"
                # assert isinstance(conf, (ConfigurationDict)), f"Got: {type(conf)}"
                # print ("SET CACHED VALUE", self, conf, key, field, val)
                self._cached_values[key] = conf


class ConfigurationDict(_Configuration):
    """Dictionary-based configuration container.

    Provides a dictionary interface to configuration values and supports
    dynamic field creation based on input values.
    """

    # meta__custom_field = "My VALUUUUuuueeeee"
    meta__loaders = [Environment()]
    meta__cache = True  # Yes by default ...
    meta__extra_fields = True
    meta__strict_cast = False

    # Optional fields
    # meta__default = NOT_SET # dict()
    # meta__extra_fields = NOT_SET # dict()

    def set_dyn_children(self, value):
        """Set up dynamic children based on input value.

        Creates fields dynamically for dictionary values that don't have
        corresponding declared fields.

        Args:
            value: Dictionary of configuration values
        """

        # Create children method
        # Check for predefined Fields
        # If additional_items == True
        # Check value
        # For each keys, check if a type exists, or field
        # Add to _extra_fields

        # For each children,
        # If class of Configuration, create child
        # If field, do noting

        # declared_fields = self.declared_fields
        children_class = self._children_class

        # Add extra fields
        child_values = value or dict()

        if isinstance(child_values, dict):

            # Look for new keys in value
            assert isinstance(
                child_values, dict
            ), f"Got {self}: {type(child_values)}: {child_values}"

            for key, _ in child_values.items():

                # Get best children_class
                field = None
                child_class = NOT_SET

                # Check if key have an existing field
                if key in self.declared_fields:
                    field = self.declared_fields[key]
                    # child_class = field.children_class
                    child_class = getattr(field, "children_class", NOT_SET)

                # Prevent unexpected childrens ...
                if not field and self._extra_fields_enabled is False:
                    msg = f"Undeclared key '{key}' for {self}, or enable extra_fields=True"
                    raise exceptions.UnknownExtraField(msg)

                if child_class is NOT_SET:
                    # Get children class form container
                    child_class = children_class

                if not field:
                    # print("REGISTER DYN FIELD", key, children_class)

                    xtra_kwargs = {}
                    if not child_class:
                        # No children_class, then it's just a field
                        child_cls = Field
                    else:
                        child_cls = FieldConf
                        xtra_kwargs = dict(children_class=child_class)

                    # Create dynamic field
                    field = child_cls(
                        key=key,
                        **xtra_kwargs,
                    )
                    self._extra_fields[key] = field

    def __iter__(self):
        yield from self.declared_fields.items()
        # yield from self._declared_values.items()


# ====================================
# Configuration Child (Dict)
# ====================================


class DeclarativeValuesMetaclass(type):
    """
    Collect Value objects declared on the base classes
    """

    def __new__(mcs, class_name, bases, attrs):
        # Collect values from current class and all bases.
        values = OrderedDict()

        # Walk through the MRO and add values from base class.
        for base in reversed(bases):
            if hasattr(base, "_declared_values"):
                values.update(base._declared_values)

        for key, value in attrs.items():
            if isinstance(value, Field):
                if value.key and key != value.key:
                    raise AttributeError(
                        "Don't explicitly set keys when declaring values"
                    )
                value.key = key
                values.update({key: value})

        attrs["_declared_values"] = values

        return super(DeclarativeValuesMetaclass, mcs).__new__(
            mcs, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(mcs, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


class Configuration(ConfigurationDict, metaclass=DeclarativeValuesMetaclass):
    """Main configuration class supporting declarative field definitions.

    This class allows fields to be declared as class attributes and provides
    a clean interface for defining configuration schemas.
    """

    meta__extra_fields = False


# ====================================
# Configuration Container (List)
# ====================================


class ConfigurationList(_Configuration):
    """List-based configuration container.

    Provides a list interface to configuration values and supports
    dynamic field creation for list elements.
    """

    # _declared_values = {}
    meta__loaders = [Environment()]
    meta__cache = True  # Yes by default ...
    meta__extra_fields = True
    meta__strict_cast = False

    def set_dyn_children(self, value):
        """Set up dynamic children based on input value.

        Creates fields dynamically for list elements.

        Args:
            value: List of configuration values
        """

        children_class = self._children_class
        child_values = value or []

        if isinstance(child_values, list):

            # Look for new keys in value
            assert isinstance(
                child_values, list
            ), f"Got {self}: {type(child_values)}: {child_values}"

            for key, _ in enumerate(child_values):

                # Get best children_class
                # field = None
                child_class = children_class

                xtra_kwargs = {}
                if not child_class:
                    # No children_class, then it's just a field
                    child_cls = Field
                else:
                    child_cls = FieldConf
                    xtra_kwargs = dict(children_class=child_class)

                # Create dynamic field
                field = child_cls(
                    key=key,
                    **xtra_kwargs,
                )
                self._extra_fields[key] = field

    def get_values(self, lvl=-1, **kwargs):
        """Get all configuration values as a list.

        Args:
            lvl: Recursion level for nested configurations
            **kwargs: Additional arguments passed to parent method

        Returns:
            List of configuration values
        """
        out = super().get_values(lvl=lvl, **kwargs)

        if isinstance(out, Mapping):
            out = list(out.values())
        return out

    def __getitem__(self, value):
        value = int(value)

        return super().__getitem__(value)
