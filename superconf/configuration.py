import copy
import inspect
import logging
from collections import OrderedDict
from pprint import pprint
from types import SimpleNamespace
from typing import Callable

from .casts import Boolean, Identity, List, Option, Tuple, evaluate

import superconf.exceptions as exceptions
from .loaders import NOT_SET, Dict, Environment, NotSet, _Value

logger = logging.getLogger(__name__)

# Shortcuts for standard casts
as_boolean = Boolean()
as_list = List()
as_tuple = Tuple()
as_option = Option
as_is = Identity()


class UnSetArg(NotSet):
    "Only forinternal methods"


UNSET_ARG = UnSetArg()
assert UNSET_ARG is not NOT_SET
# assert UNSET_ARG is not NOT_SET
# assert UNSET_ARG == NOT_SET


# def getconf(item, default=NOT_SET, cast=None, loaders=None):
#     """
#     :param item:    Name of the setting to lookup.
#     :param default: Default value if none is provided. If left unset,
#                     loading a config that fails to provide this value
#                     will raise a UnknownConfiguration exception.
#     :param cast:    Callable to cast variable with. Defaults to type of
#                     default (if provided), identity if default is not
#                     provided or raises TypeError if provided cast is not
#                     callable.
#     :param loaders: A list of loader instances in the order they should be
#                     looked into. Defaults to `[Environment()]`
#     """
#     if callable(cast):
#         cast = cast
#     elif cast is None and (default is NOT_SET or default is None):
#         cast = as_is
#     elif isinstance(default, bool):
#         cast = as_boolean
#     elif cast is None:
#         cast = type(default)
#     else:
#         raise TypeError("Cast must be callable")

#     for loader in loaders:
#         try:
#             return cast(loader[item])
#         except KeyError:
#             continue

#     if default is NOT_SET:
#         raise UnknownConfiguration("Configuration '{}' not found".format(item))

#     return cast(default)


class Field:
    def __init__(
        self,
        key: str = None,
        *,
        help: str = "",
        default: NOT_SET = NOT_SET,
        cast: Callable = None,
    ):
        """
        :param key:     Name of the value used in file or environment
                        variable. Set automatically by the metaclass.
        :param default: Default value if none is provided. If left unset,
                        loading a config that fails to provide this value
                        will raise a UnknownConfiguration exception.
        :param cast:    Callable to cast variable with. Defaults to type of
                        default (if provided), identity if default is not
                        provided or raises TypeError if provided cast is not
                        callable.
        :param help:    Plain-text description of the value.
        """
        self.key = key
        self.help = help
        self.default = default
        self.cast = cast

    def __get__(self, conf_instance, owner):
        if conf_instance:
            return conf_instance.get_field_value(key=self.key, field=self)
        return self

    def __repr__(self):
        return '{}(key="{}", help="{}")'.format(
            self.__class__.__name__, self.key, self.help
        )

    def is_container(self):
        children_class = getattr(self, "children_class", None)
        if children_class is not None:
            return True
        return False

    def resolve_value(
        self,
        conf_instance,
        value=NOT_SET,
        default=NOT_SET,
        cast=NOT_SET,
        loaders=NOT_SET,
        **kwargs,
    ):
        "Create a children"

        key = self.key
        assert key, f"Got: {type(key)} {key}"

        # Process defaults
        default_from = ["args"]
        if default is NOT_SET and isinstance(conf_instance._default, dict):
            # Fetch default from container

            # default2 = default
            try:
                default = conf_instance.query_inst_cfg(
                    "default", override=kwargs, default=NOT_SET
                )[key]
                default_from.append("conf_instance_query")
            except KeyError:
                pass

        if default is NOT_SET:
            # Fetch default from field
            default = self.default
            default_from.append("field_instance")

        # Process value
        if value is NOT_SET:
            # Fetch default from container
            try:
                value = conf_instance._value[key]
            except (TypeError, KeyError):
                pass

        # Process cast
        if cast is NOT_SET:
            cast = self.cast
        if cast is NOT_SET:
            cast = conf_instance._cast

        # Process loaders
        if loaders is NOT_SET:
            loaders = conf_instance._loaders
        if value:
            loaders.insert(0, _Value({key: value}))

        # Determine cast method
        if callable(cast):
            cast = cast
        elif cast is None and (default is NOT_SET or default is None):
            cast = as_is
        elif isinstance(default, bool):
            cast = as_boolean
        elif cast is None:
            cast = type(default)
        elif cast is NOT_SET:
            if default is NOT_SET or default is None:
                cast = type(default)
            else:
                cast = as_is
        else:
            raise TypeError(f"Cast must be callable, got: {type(cast)}")

        # Process things
        result = NOT_SET
        for loader in loaders:
            try:
                # print (f"  > LOADER: try search in {loader} key: {key}")
                result = loader.getitem(self, key, **kwargs)

            except (KeyError, TypeError) as err:
                # print (f"{self}: Loader {key} {loader.__class__.__name__} failed with error: {type(err)}{err}")
                continue

            if result is not NOT_SET:
                result = cast(result)
                break

        # Nothing found in all loaders, then fallback on default
        results_from = []
        if result is NOT_SET:
            result = value
            results_from.append("from_value")
        if result is NOT_SET:
            result = default
            results_from.append("from_default")
        if result is NOT_SET:
            try:
                result = cast(result)
                results_from.append("casted")
            except ValueError:
                pass

        meta = SimpleNamespace(
            cast=cast,
            default=default,
            loaders=loaders,
            value=result,
            results_from=results_from,
            default_from=default_from,
        )

        return result, meta


class FieldBool(Field):
    "Boolean field"

    cast = as_boolean


class FieldConf(Field):
    "Nested Config"

    def __init__(
        self,
        key: str = None,
        children_class: NOT_SET = NOT_SET,
        **kwargs,
    ):

        super(FieldConf, self).__init__(key, **kwargs)
        self.children_class = children_class


# Compatibility with classyconf
Value = Field


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


class Configuration(metaclass=DeclarativeValuesMetaclass):

    # class ConfigurationCtrl:
    "Controller"

    meta__custom_field = "My VALUUUUuuueeeee"
    meta__loaders = [Environment()]
    meta__cache = True  # Yes by default ...
    meta__extra_fields = False

    # Optional fields
    # meta__default = NOT_SET # dict()
    # meta__extra_fields = NOT_SET # dict()

    class Meta:
        "Class to store class overrides"

    def __init__(self, *, key=None, parent=None, value=NOT_SET, meta=None, **kwargs):
        self.key = key
        self._parent = parent
        self._value = value

        # As this can be updated during runtime ...
        self._declared_values = self._declared_values
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

    def set_values(self, value):
        "Set a value"

        # Instanciate containers fields - Automatic
        for key, field in self.declared_fields.items():

            if field.is_container():
                # Create child then
                try:
                    val = value.get(key, NOT_SET)
                except AttributeError:
                    val = NOT_SET

                # print ("AUTOMATIC CREATE CHILD CONTAINER", key, field, val)
                conf = self.create_child(key, field, value=val)
                assert isinstance(conf, (Configuration)), f"Got: {type(conf)}"
                # print ("SET CACHED VALUE", self, conf, key, field, val)
                self._cached_values[key] = conf

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
        raise  exceptions.UnknownSetting(msg)

    def query_parent_cfg(self, name, as_subkey=False, cast=None, default=UNSET_ARG):
        "Query parent config"

        # Fast exit or raise exception
        if not self._parent:
            if default is not UNSET_ARG:
                return default
            msg = f"Setting '{name}' has not been declared in hierarchy of '{repr(self)}'"
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

    # Field compat API
    @property
    def default(self):
        "Temporary property to access to self._default"
        return self._default

    @property
    def cast(self):
        "Temporary property to access to self._default"
        return self._cast

    @property
    def declared_fields(self):
        out = {}
        if self._extra_fields:
            # Add extra fields
            out.update(self._extra_fields)

        # Always use explicit fields
        out.update(self._declared_values)
        return out

    # Field compatibility layer !
    # This basically respect default python behavior ...
    def __get__(self, conf_instance, owner):
        # if conf_instance:
        #     return conf_instance.get_field_value(field=self)
        return self

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
                raise exceptions.UndeclaredField("Configuration '{}' not found".format(key))
            assert key == field.key, f"Got: {key} != {field.key}"
            key = field.key

        if key is None:
            key = field.key

        # Check in cache
        if self._cache and key in self._cached_values:
            return self._cached_values[key]

        conf = self.create_child(key, field, **kwargs)
        assert isinstance(
            conf, (type(None), dict, bool, int, str, Configuration)
        ), f"Got: {type(conf)}"

        if self._cache:
            self._cached_values[key] = conf
            # print("CACHE CHILD", self, key, conf)
        return conf

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

    def get_value(self, key, lvl=-1, **kwargs):
        assert isinstance(key, str)
        return self.get_field_value(key, **kwargs)

    def get_values(self, lvl=-1, **kwargs):

        if lvl == 0:
            return self

        out = {}
        for key, obj in self.declared_fields.items():
            val = self.get_field_value(key)
            if isinstance(val, Configuration):
                val = val.get_values(lvl=lvl - 1)

            out[key] = val

        return out

    def reset(self):
        """Anytime you want to pick up new values call this function."""
        for loader in self._loaders:
            loader.reset()
        self._cached_values = {}

    # def _iterate_declared_values(self):
    #     return self.declared_fields

    # class Configuration(ConfigurationCtrl, metaclass=DeclarativeValuesMetaclass):
    #     """
    #     Encapsulates settings than can be loaded from different
    #     sources.
    #     """

    def __iter__(self):
        yield from self.declared_fields.items()
        # yield from self._declared_values.items()

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

    def __getitem__(self, value):
        return self.declared_fields[value].__get__(self, self.__class__)


class ConfigurationDict(Configuration, metaclass=DeclarativeValuesMetaclass):
    "Variadic configuration"

    meta__extra_fields = True
