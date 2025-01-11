import copy
import inspect
import logging
from collections import OrderedDict
from pprint import pprint
from typing import Callable

from classyconf.casts import Boolean, Identity, List, Option, Tuple, evaluate

from .exceptions import UnknownConfiguration
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


def getconf(item, default=NOT_SET, cast=None, loaders=None):
    """
    :param item:    Name of the setting to lookup.
    :param default: Default value if none is provided. If left unset,
                    loading a config that fails to provide this value
                    will raise a UnknownConfiguration exception.
    :param cast:    Callable to cast variable with. Defaults to type of
                    default (if provided), identity if default is not
                    provided or raises TypeError if provided cast is not
                    callable.
    :param loaders: A list of loader instances in the order they should be
                    looked into. Defaults to `[Environment()]`
    """
    if callable(cast):
        cast = cast
    elif cast is None and (default is NOT_SET or default is None):
        cast = as_is
    elif isinstance(default, bool):
        cast = as_boolean
    elif cast is None:
        cast = type(default)
    else:
        raise TypeError("Cast must be callable")

    for loader in loaders:
        try:
            return cast(loader[item])
        except KeyError:
            continue

    if default is NOT_SET:
        raise UnknownConfiguration("Configuration '{}' not found".format(item))

    return cast(default)


class Field:
    def __init__(
        self,
        key: str = None,
        *,
        help: str = "",
        default: NOT_SET = NOT_SET,
        children_class: NOT_SET = NOT_SET,
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
        self.children_class = children_class

    def __get__(self, conf_instance, owner):
        if conf_instance:
            return conf_instance.get_field_value(field=self)
        return self

    def __repr__(self):
        return '{}(key="{}", help="{}")'.format(
            self.__class__.__name__, self.key, self.help
        )


# Compatibility
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

    # Optional fields
    # meta__default = NOT_SET # dict()
    # meta__extra_fields = NOT_SET # dict()

    class Meta:
        "Class to store class overrides"

    def __init__(self, *, key=None, parent=None, value=None, meta=None, **kwargs):
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
        self._cache = self.query_inst_cfg("cache", override=kwargs)

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

        # print ("NEW INSTANCE CREATED", self, self.key, "loaders=", self._loaders)

        # Init children IF value is provided !!!
        value = self._value
        # _children =
        if isinstance(value, dict):
            for key, val in value.items():
                # self.get_field_value(key=key, value=val)

                field = Field()
                if key in self.declared_fields:
                    field = self.declared_fields[key]
                elif self._extra_fields_enabled is True:
                    pprint(self._children_class)
                    # field = self._children_class(key=key, parent=self)
                    field = Field(key=key)  # , children_class=self._children_class)
                else:
                    raise Exception("Extra fields detected ")

                assert isinstance(field, Field), "Yeahhh"
                # out = self.getconf3(key=key, field=field, value=val)
                # self._extra_fields[key] = out
                self._extra_fields[key] = field

    # def declared_fields(self):
    #     out = {}
    #     if self._extra_fields:

    def query_inst_cfg(self, *args, cast=None, **kwargs):
        "Temporary wrapper"
        out = self._query_inst_cfg(*args, **kwargs)
        # try:
        #     out = self._query_inst_cfg(*args, **kwargs)
        # except Exception:
        #     out = cast()
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

    @classmethod
    def _query_cls_cfg(cls, *args, **kwargs):
        "Temporary class method"
        out = cls._query_inst_cfg(cls, *args, **kwargs)
        if isinstance(out, (dict, list)):
            out = copy.copy(out)
        return out

    def _query_inst_cfg(self, name, override=None, parents=False, default=UNSET_ARG):
        "Query instance settings, or fallback on class settings"

        # Fetch from dict override, if providedchildren_class
        if isinstance(override, dict):
            val = override.get(name, NOT_SET)
            if val is not NOT_SET:
                return val

        # Fetch from self._NAME
        # Good for initial setup, if write mode is required
        val = getattr(self, f"_{name}", NOT_SET)
        if val is not NOT_SET:
            return val

        # Python class params
        # Good for class overrides
        cls = self
        if hasattr(cls, "Meta"):
            val = getattr(cls.Meta, name, NOT_SET)
            if val is not NOT_SET:
                # print ("SELF CLASS Meta retrieval for: {cls}" , name, val)
                return val

        # Fetch from self.meta__NAME
        # Python class inherited params (good for defaults)
        val = getattr(self, f"meta__{name}", NOT_SET)
        if val is not NOT_SET:
            return val

        # Fetch from self.NAME
        val = getattr(self, name, NOT_SET)
        if val is not NOT_SET:
            assert False, "Deprecated"
            return val

        if default is not UNSET_ARG:
            return default

        raise Exception(f"Missing config: {name} in {repr(self)}")

    def query_parent_cfg(self, name, as_subkey=False, cast=None, default=UNSET_ARG):
        "Query parent config"

        # Fast exit or raise exception
        if not self._parent:
            if default is not UNSET_ARG:
                return default
            raise Exception(f"Missing config: {name} in {repr(self)}")

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
                raise UnknownConfiguration("Configuration '{}' not found".format(key))
            assert key == field.key, f"Got: {key} != {field.key}"
            key = field.key

        if key is None:
            key = field.key

        # Check in cache
        if self._cache and key in self._cached_values:
            return self._cached_values[key]

        # # Check in value
        # if isinstance(self._value, dict) and key in self._value:
        #     # But return an instance instead !!!
        #     out = self._value[key]
        #     print ("RETURNING", self, key, out)
        #     return out

        conf = self.getconf3(key, field, **kwargs)
        assert isinstance(
            conf, (type(None), dict, bool, int, str, Configuration)
        ), f"Got: {type(conf)}"

        if self._cache:
            self._cached_values[key] = conf
            print("CACHE CHILD", self, key, conf)
        return conf

    # This should be split if field has children or not ...
    def getconf3(self, key, field, **kwargs):
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

        # Default children_class
        # children_class = self.query_inst_cfg(
        #     "children_class",
        #     override=kwargs,
        #     default=NOT_SET,
        # )
        children_class = self._children_class
        if children_class is NOT_SET and field:
            children_class = field.children_class

        # Default lookup
        default = self._default
        if default is NOT_SET and field:
            default = field.default

        # Value lookup
        value = NOT_SET
        if isinstance(self._value, dict) and key in self._value:
            value = self._value[key]
        loader_value = _Value(value)
        # loader_value = Dict(value)

        # Load cast
        cast = self.query_inst_cfg(
            "cast",
            override=kwargs,
            default=NOT_SET,
        )
        if cast is NOT_SET and field:
            cast = field.cast

        # Load loaders
        loaders = list(self._loaders)
        # loaders = self.query_inst_cfg(
        #     "loaders",
        #     override=kwargs,
        #     default=NOT_SET,
        # )

        # print ("LOADERS:")
        # pprint(loaders)
        if loaders is NOT_SET and field:
            # loaders = field.loaders
            loaders = []
        # loaders.insert(0, loader_value)

        assert key, f"Got: {type(key)} {key}"

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

        # Helper to create a children in case of ...
        # def create_children():

        # Create a child if requested ...
        child_kwargs = {}
        if children_class:

            child_kwargs = dict(
                default=default,
                value=value,
                cast=cast,
                # loaders=loaders,
                # child_loaders=child_loaders,
                # children_class=children_class,
            )

        # Try each loaders
        # TOFIX: Skip loader step when values are provided ? Nope, we may want to
        # override a specif value on a full config ...
        found = False
        out = NOT_SET
        for loader in loaders:
            # print (f"LOOK OF {key} in", loader)

            try:
                # print (f"  > LOADER: try search in {loader} key: {key}")
                out = cast(loader.getitem(self, key, **child_kwargs))
                if out is not NOT_SET:
                    break

            except (KeyError, TypeError) as err:
                # print (f"{self}: Loader {key} {loader.__class__.__name__} failed with error: {type(err)}{err}")
                continue

        # Nothing found in all loaders, then fallback on default
        if out is NOT_SET:
            out = value

        # Create a child if requested ...
        if children_class:

            child_kwargs = dict(
                default=default,
                value=value,
                cast=cast,
                # loaders=loaders,
                # child_loaders=child_loaders,
                # children_class=children_class,
            )

            _default = {}
            try:
                _default = out.get(key, {})
            except AttributeError:
                pass

            print("CREATE NEW CHILD WIRH", key, child_kwargs)
            out = children_class(
                key=key,
                parent=self,
                # loaders=[Dict(_default)],
                # loaders=loaders,
                value=value,
                meta=child_kwargs,
            )

            return out

            # if out is not NOT_SET:
            #     # Create a child if requested ...
            #     if children_class:
            #         _default = {}
            #         try:
            #             _default = out.get(key, {})
            #         except AttributeError:
            #             pass
            #         # print ("CREATE NEW CHILD WIRH", key, _default)
            #         out = children_class(
            #             key=key,
            #             parent=self,
            #             # loaders=[Dict(_default)],
            #             loaders=loaders,
            #             value=value,
            #         )
            #     return out

        # If nothing found, return an empty/default children.
        # If no data found in loaders, then create a children object
        # and return it. This allow nested configs
        # if children_class:
        #     assert inspect.isclass(children_class)

        #     # self should be a subitem if provided
        #     # loaders should have child class
        #     child_inst = children_class(
        #         key=key,
        #         parent=self,
        #         loaders=child_loaders,
        #         value=value,
        #     )
        #     # print("CREATE NEW CHILDREN instance", id(child_inst), children_class, loaders)
        #     return child_inst

        if default is NOT_SET:
            raise UnknownConfiguration("Configuration '{}' not found".format(key))

        return cast(default)

    def get_value(self, key, lvl=-1, **kwargs):
        assert isinstance(key, str)
        return self.get_field_value(key, **kwargs)

    def get_values(self, lvl=-1, **kwargs):

        if lvl == 0:
            return self

        out = {}
        for key, obj in self.declared_fields.items():
            # val = obj #.get_values(lvl=lvl-1)
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
