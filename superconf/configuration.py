from collections import OrderedDict
from typing import Callable
import inspect
import logging

from classyconf.casts import Boolean, Identity, List, Option, Tuple, evaluate
from classyconf.exceptions import UnknownConfiguration
from classyconf.loaders import NOT_SET, Environment, Dict, NotSet

from pprint import pprint


logger = logging.getLogger(__name__)

# Shortcuts for standard casts
as_boolean = Boolean()
as_list = List()
as_tuple = Tuple()
as_option = Option
as_is = Identity()


class UnSetArg(NotSet):
    "Only forinternal methods"

UNSET_ARG=UnSetArg()
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


# Check best config:

# first(
#     cache = bool or NOT_SET,
#     self._cache = bool or NOT_SET,

# )


def get_param(name, obj_meta=None, obj=None, override=None, unset=NOT_SET):
    "Return an object param, from override, Meta, or class attr"

    # if name == "loaders":
    #     print ("DUMP HERE")

    # Look first in overrides
    if isinstance(override, dict):
        if name in override:
            val = override[name]
            if val is not NOT_SET:
                return val

    # Look in parent Meta
#     if inspect.isclass(obj_meta):
#         print ("YOOOO")
#     if hasattr(obj_meta, "Meta"):
#         print ("YESSS", type(obj_meta))
#     # if isinstance(obj_meta, Configuration):
# #  or inspect.isclass(obj_meta)

    # print ("INSPECT", type(obj_meta), ":", name)
    if hasattr(obj_meta, "Meta"):
        val = getattr(obj_meta.Meta, name, NOT_SET)
        if val is not NOT_SET:
            # assert False
            # print ("Meta retrieval for:" , name, val)
            return val

    # Look in class attributes
    if obj:
        # pprint (obj.__dict__)
        val = getattr(obj, name, NOT_SET)
        if val is not NOT_SET:
                return val

        val = getattr(obj, f"_{name}", NOT_SET)
        if val is not NOT_SET:
                return val

    return unset
    # assert False, f"Unknown param: {name}"

# def getconf2(key, config, field, **kwargs):
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

#     # item = field.key
#     # item = key
#     # default= field.default 
    
#     child = NOT_SET
#     if child == NOT_SET and config:
#         child = get_param("child", obj_meta=config, obj=config, override=kwargs)
#     if child == NOT_SET and field:
#         child = field.child


#     default2= NOT_SET
#     if field:
#         default2 = field.default
#     default = NOT_SET
#     if default == NOT_SET and kwargs and "default" in kwargs:
#         default = kwargs["default"]
#     if default == NOT_SET and config:
#         default = get_param("default", obj_meta=config, obj=config, override=kwargs)
#     if default == NOT_SET and field:
#         default = field.default
    
#     # if not default == default2:
#     #     print ("MISMATCH", f"Got: {default} VS {default2}")

#     # print ("default=", default)

#     cast = NOT_SET
#     if cast == NOT_SET and kwargs and "cast" in kwargs:
#         cast = kwargs["cast"]
#     # if cast == NOT_SET and config:
#     #     cast = get_param("cast", obj_meta=config, obj=config, override=kwargs)
#     if cast == NOT_SET and field:
#         cast = field.cast


#     loaders = NOT_SET
#     if loaders == NOT_SET and kwargs and "loaders" in kwargs:
#         loaders = kwargs["loaders"]

#     if loaders == NOT_SET and config:
#         loaders = get_param("loaders", obj=config)
#     # if loaders == NOT_SET and field:
#     #     loaders = field.loaders
#     # print ("LOADERS", type(config), key,  loaders)


#     # loaders2= config._loaders
#     # assert loaders == loaders2, f"Got: {loaders} VS {loaders2}"




#     assert key, f"Got: {type(key)} {key}"


#     if callable(cast):
#         cast = cast
#     elif cast is None and (default is NOT_SET or default is None):
#         cast = as_is
#     elif isinstance(default, bool):
#         cast = as_boolean
#     elif cast is None:
#         cast = type(default)
#     elif cast is NOT_SET:
#         if (default is NOT_SET or default is None):
#             cast = type(default)
#         else:
#             cast = as_is
#     else:
#         raise TypeError(f"Cast must be callable, got: {type(cast)}")

    
#     # DEtermine child loader
#     if child:
#         child_loaders = get_param("loaders", obj_meta=child)

#     for loader in loaders:
#         # print (f"LOOK OF {key} in", loader)
#         out = NOT_SET
#         try:
#             # print (f"  > LOADER: try search in {loader} key: {key}")
#             out = cast(loader[key])
#         except KeyError:
#             continue

#         if out is not NOT_SET:
#             # Create a child if requested ...
#             if child:
#                 _default = {}
#                 try:
#                     _default = out.get(key, {})
#                 except AttributeError:
#                     pass
#                 # print ("CREATE NEW CHILD WIRH", key, _default)
#                 out = child(
#                     key=key,
#                     parent = config,
#                     loaders = [
#                         Dict(_default)
#                     ],
#                 )
#             return out

#     # If nothing found, return an empty/default children.
#     # If no data found in loaders, then create a children object
#     # and return it. This allow nested configs
#     if child:
#         assert inspect.isclass(child)

#         # loaders = get_param("loaders", obj_meta=child)

#         # config should be a subitem if provided
#         # loaders should have child class
#         # assert False
#         child_inst = child(
#             key=key, 
#             parent = config,
#             loaders = child_loaders,
#             # loaders = [
#             #     Dict({})
#             # ],
#             )
#         # print("CREATE NEW CHILDREN instance", id(child_inst), child, loaders)
#         return child_inst
#         # assert False, "Create a new child instance"

#     if default is NOT_SET:
#         raise UnknownConfiguration("Configuration '{}' not found".format(key))

#     return cast(default)



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


class ConfigurationCtrl():
    "Controller"

    meta__custom_field = "My VALUUUUuuueeeee"
    meta__loaders = [Environment()]
    meta__cache = False

    # Optional fields
    # meta__default = NOT_SET # dict()
    # meta__extra_fields = NOT_SET # dict()

    class Meta:
        "Class to store class overrides"
    #     loaders = None
    #     cache = False
        

    # def __init__(self, *, key=None, parent=None, value=None, loaders=NOT_SET, cache=NOT_SET):
    def __init__(self, *, key=None, parent=None, value=None, **kwargs):
        self._key = key
        self._parent = parent
        self._value = value

        kwargs.update(
            dict(
                key=key,
                # loaders=loaders,
                # cache=cache,
                parent=parent,
            )
        )

        self._loaders = self.query_inst_cfg("loaders", override=kwargs)
        self._cache = self.query_inst_cfg("cache", override=kwargs)
        self._extra_fields = self.query_inst_cfg("extra_fields", override=kwargs, default=NOT_SET)
        

        self._default = self.query_inst_cfg("default", override=kwargs, default=NOT_SET)
        if self._default is NOT_SET:
            self._default = self.query_parent_cfg("default", as_subkey=True, default=NOT_SET)



        # if self._key == "resources":
        #     print("\n\n==== DEBUG RESOURCES DEFAULTS")
        #     self._default = self.query_inst_cfg("default", override=kwargs, default=NOT_SET)

        #     if self._default is NOT_SET:
        #         self._default = self.query_parent_cfg("default", as_subkey=True, default=NOT_SET)

        # else:
        #     self._default = self.query_inst_cfg("default", override=kwargs, default=NOT_SET)

        print ("REGISTERED DEFAULT, ", self, "|", self._key, "|",  self._default)
        # self._default = self._default2

        # assert 

        # # OLD TO REMOVE

        # _loaders = getattr(self.Meta, "loaders", None)
        # if _loaders is None:
        #     _loaders = [Environment()]
        # if loaders:
        #     _loaders = loaders

        # # _loaders2 = 
        # self._loaders = _loaders
        # # assert self._loaders == self._loaders2, f"{self._loaders} VS {self._loaders2}, Probably too strict"
        # assert [x.__class__ for x in self._loaders] == [x.__class__ for x in self._loaders2], f"{self._loaders} VS {self._loaders2}, Probably too strict"

        # # print ("PRE FAIL", self)
        # # tmp = self.query_inst_cfg("cache", override=kwargs, default=False)
        # # pprint (tmp)
        # self._cache2 = any(
        #     (
        #         getattr(self.Meta, "cache", False),
        #         cache,
        #     )
        # )
        # self._cached_values = {}
        # assert self._cache2 == self._cache





    def query_inst_cfg(self, *args, cast=None, **kwargs):
        "Temporary wrapper"
        out = self._query_inst_cfg(*args, **kwargs)
        # try:
        #     out = self._query_inst_cfg(*args, **kwargs)
        # except Exception:
        #     out = cast()

        if cast is not None:
            # Try to cast if asked
            if not out:
                out = cast()
            assert isinstance(out, cast), f"Wrong type for config {name}, expected {cast}, got: {type(out)} {out}"
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



    # def _query_inst_cfg(self, name, override=None, parents=False, default=UNSET_ARG):

    def query_parent_cfg(self, name, as_subkey=False, cast=None, default=UNSET_ARG):
        "Temporary wrapper"

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
                val = val.get(self._key, NOT_SET)

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
            assert isinstance(out, cast), f"Wrong type for config {name}, expected {cast}, got: {type(out)} {out}"
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





    # def get_field_value_V1(self, field, **kwargs):

    #     # assert isinstance(field, Field), f"Got {type(field)}: {field}"

    #     # print("CALL", field, kwargs)
    #     key = None
    #     if isinstance(field, (str, int)):
    #         key = field
    #         field = self.declared_fields.get(key, None)
    #         # if field == None:
    #         #     raise UnknownConfiguration("Configuration '{}' not found".format(key))

    #     if isinstance(field, Field):
    #         key = field.key

    #     # assert isinstance(field, (Field, type(None))), f"Got {type(field)}: {field}"
    #     assert isinstance(key, str), f"Got {type(key)}: {key}"
        
    #     cache_enabled = get_param("cache", obj=self, obj_meta=self, override=kwargs)
    #     assert cache_enabled == self._cache


    #     if cache_enabled and key in self._cached_values:
    #         return self._cached_values[key]

    #     # print("Get cofnig for key:", key)
    #     # conf = getconf2(key, self, field, _parent=self, **kwargs)
    #     conf = getconf2(key, self, field, **kwargs)
    #     # print("DOES NOT PASS")
    #     if cache_enabled:
    #         self._cached_values[key] = conf
    #     return conf





    # def _get_field_value(self, field):

    #     key = field.key
    #     assert key in self.declared_fields, "Unregistred field access"
    #     return self.get_field_value(key)


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
            assert key == field.key
            key = field.key

        if key is None:
            key = field.key

        # Check in cache
        if self._cache and key in self._cached_values:
            return self._cached_values[key]

        # conf = getconf2(key, self, field, **kwargs)
        conf = self.getconf3(key, field, **kwargs)
        assert isinstance(conf, (type(None), dict, bool, int, str, Configuration)), f"Got: {type(conf)}"

        if self._cache:
            self._cached_values[key] = conf
        return conf





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


        # Default lookup child_cls
        #  - kwargs default override
        #  - current object defaults
        #      - Must be a dict, and the key must be present or NEXT
        #  - child
        #      - DEfault must be set
        #  - UNSET        
        children_class = self.query_inst_cfg(
            "children_class",
            override=kwargs,
            default=NOT_SET,
            )
        if children_class is NOT_SET and field:
            children_class = field.children_class


        # Default lookup
        #  - kwargs default override
        #  - current object defaults
        #      - Must be a dict, and the key must be present or NEXT
        #  - child
        #      - DEfault must be set
        #  - UNSET
        default = self._default
        if default is NOT_SET and field:
            default = field.default

        # cast = NOT_SET
        # if cast == NOT_SET and kwargs and "cast" in kwargs:
        #     cast = kwargs["cast"]
        # # if cast == NOT_SET and self:
        # #     cast = get_param("cast", obj_meta=self, obj=self, override=kwargs)
        # if cast == NOT_SET and field:
        #     cast = field.cast

        cast = self.query_inst_cfg(
            "cast",
            override=kwargs,
            default=NOT_SET,
            )
        if cast is NOT_SET and field:
            cast = field.cast

        
        # assert cast == cast2


        loaders = self.query_inst_cfg(
            "loaders",
            override=kwargs,
            default=NOT_SET,
            )
        if loaders is NOT_SET and field:
            # loaders = field.loaders
            loaders = []

        # loaders = NOT_SET
        # if loaders == NOT_SET and kwargs and "loaders" in kwargs:
        #     loaders = kwargs["loaders"]

        # if loaders == NOT_SET and self:
        #     loaders = get_param("loaders", obj=self)

        # if loaders == NOT_SET and field:
        #     loaders = field.loaders
        # print ("LOADERS", type(self), key,  loaders)


        # loaders2= self._loaders
        # assert loaders == loaders2, f"Got: {loaders} VS {loaders2}"




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
            if (default is NOT_SET or default is None):
                cast = type(default)
            else:
                cast = as_is
        else:
            raise TypeError(f"Cast must be callable, got: {type(cast)}")

        
        # DEtermine child loader
        if children_class:
            child_loaders = get_param("loaders", obj_meta=children_class)

        for loader in loaders:
            # print (f"LOOK OF {key} in", loader)
            out = NOT_SET
            try:
                # print (f"  > LOADER: try search in {loader} key: {key}")
                out = cast(loader[key])
            except (KeyError, TypeError):
                continue

            if out is not NOT_SET:
                # Create a child if requested ...
                if children_class:
                    _default = {}
                    try:
                        _default = out.get(key, {})
                    except AttributeError:
                        pass
                    # print ("CREATE NEW CHILD WIRH", key, _default)
                    out = children_class(
                        key=key,
                        parent = self,
                        loaders = [
                            Dict(_default)
                        ],
                    )
                return out

        # If nothing found, return an empty/default children.
        # If no data found in loaders, then create a children object
        # and return it. This allow nested configs
        if children_class:
            assert inspect.isclass(children_class)

            # loaders = get_param("loaders", obj_meta=children_class)

            # self should be a subitem if provided
            # loaders should have child class
            # assert False
            child_inst = children_class(
                key=key, 
                parent = self,
                loaders = child_loaders,
                # loaders = [
                #     Dict({})
                # ],
                )
            # print("CREATE NEW CHILDREN instance", id(child_inst), children_class, loaders)
            return child_inst
            # assert False, "Create a new children_class instance"

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
                val = val.get_values(lvl=lvl-1)
            
            out[key] = val
        
        return out


    def reset(self):
        """Anytime you want to pick up new values call this function."""
        for loader in self._loaders:
            loader.reset()
        self._cached_values = {}


    # def _iterate_declared_values(self):
    #     return self.declared_fields


class Configuration(ConfigurationCtrl, metaclass=DeclarativeValuesMetaclass):
    """
    Encapsulates settings than can be loaded from different
    sources.
    """




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
