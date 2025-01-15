import copy
import inspect
import logging
from collections import OrderedDict

# from collections import Mapping, Sequence
from collections.abc import Mapping, Sequence
from pprint import pprint
from types import SimpleNamespace
from typing import Callable

import superconf.exceptions as exceptions
from .common import FAIL, NOT_SET, UNSET_ARG, NotSet
from .loaders import Environment

from .fields import Field, FieldConf

logger = logging.getLogger(__name__)


class DeclarativeValuesMetaclass(type):
    """
    Collect Value objects declared on the base classes
    """

    def __new__(self, class_name, bases, attrs):
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

        return super(DeclarativeValuesMetaclass, self).__new__(
            self, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


class _ConfigurationBase():
    "Generic configuration"



    class Meta:
        "Class to store class overrides"


    def __init__(self, key=None, value=NOT_SET, parent=None):
        self.key = key
        self._parent = parent
        self._value = value

        self._cache = True  # TOFIX


    # Instance config management
    # ----------------------------

    def query_inst_cfg(self, *args, cast=None, **kwargs):
        "Temporary wrapper"
        out, query_from = self._query_inst_cfg(*args, **kwargs)
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
            ), f"Wrong type for config {name}, expected {cast}, got: {type(out)} {out}"
        return out

    # @classmethod
    # def _query_cls_cfg(cls, *args, **kwargs):
    #     "Temporary class method"
    #     out = cls._query_inst_cfg(cls, *args, **kwargs)
    #     if isinstance(out, (dict, list)):
    #         out = copy.copy(out)
    #     return out

    def _query_inst_cfg(self, name, override=None, parents=False, default=UNSET_ARG):
        "Query instance settings, or fallback on class settings"
        query_from = []

        # Fetch from dict override, if providedchildren_class
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

        msg = f"Setting '{name}' has not been declared before being used in '{repr(self)}', tried to query: {query_from}"
        raise exceptions.UnknownSetting(msg)

    def query_parent_cfg(self, name, as_subkey=False, cast=None, default=UNSET_ARG):
        "Query parent config"

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
            val = self._parent._query_inst_cfg(name, default=NOT_SET)
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




class _Configuration(_ConfigurationBase):

    _declared_values = {}


    def __init__(self, *, key=None, value=NOT_SET, parent=None, meta=None, **kwargs):

        super(_Configuration, self).__init__(key=key, value=value, parent=parent)


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
        assert isinstance(key, str)
        return self.get_field_value(key, **kwargs)



    def reset(self):
        """Anytime you want to pick up new values call this function."""
        for loader in self._loaders:
            loader.reset()
        self._cached_values = {}



    def get_field_value(self, key=None, field=None, default=UNSET_ARG, **kwargs):

        # Parse input
        if field is None and key is None:
            assert False, "BUG herrrrr"

        if field is None:
            assert isinstance(key, (str, int))

            field = self.declared_fields.get(key, None)
            if field is None:
                if default is not UNSET_ARG:
                    return default
                raise exceptions.UndeclaredField(
                    "Configuration '{}' not found".format(key)
                )
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
        for key, obj in self.declared_fields.items():
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
                    print ("BUG HERE ON KEY", self, key, value)
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

    # class ConfigurationCtrl:
    "Controller"

    # meta__custom_field = "My VALUUUUuuueeeee"
    meta__loaders = [Environment()]
    meta__cache = True  # Yes by default ...
    meta__extra_fields = True
    meta__strict_cast = False


    # Optional fields
    # meta__default = NOT_SET # dict()
    # meta__extra_fields = NOT_SET # dict()


    def set_dyn_children(self, value):
        "Set a value"

        # Create children method
        # Check for predefined Fields
        # If additional_items == True
        # Check value
        # For each keys, check if a type exists, or field
        # Add to _extra_fields

        # For each children,
        # If class of Configuration, create child
        # If field, do noting

        declared_fields = self.declared_fields
        children_class = self._children_class

        # Add extra fields
        child_values = value or dict()

        if isinstance(child_values, dict):

            # Look for new keys in value
            assert isinstance(
                child_values, dict
            ), f"Got {self}: {type(child_values)}: {child_values}"

            for key, val in child_values.items():

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


class Configuration(ConfigurationDict, metaclass=DeclarativeValuesMetaclass):
    "Variadic configuration"

    meta__extra_fields = False
