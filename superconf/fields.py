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

from .casts import (
    AsBoolean,
    AsDict,
    AsIdentity,
    AsInt,
    AsList,
    AsOption,
    AsTuple,
    evaluate,
)
from .common import FAIL, NOT_SET, UNSET_ARG, NotSet
from .loaders import _Value

# Shortcuts for standard casts
as_boolean = AsBoolean()
as_int = AsInt()
as_list = AsList()
as_dict = AsDict()
as_tuple = AsTuple()
as_option = AsOption
as_is = AsIdentity()


class Field:

    cast = None

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
        self.cast = cast or self.cast

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
        assert isinstance(key, (str, int)), f"Got: {type(key)} {key}"

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
            except (TypeError, KeyError):  # For dict
                pass
            except IndexError:  # For list
                pass

        # Process cast
        cast_from = []
        if cast is NOT_SET:
            cast = self.cast
            cast_from.append(f"field_attr:{self}.cast")
        if cast is NOT_SET:
            cast = conf_instance._cast
            cast_from.append(f"conf_attr:{conf_instance}._cast")

        # Process loaders
        if loaders is NOT_SET:
            loaders = conf_instance._loaders
        if value:
            loaders.insert(0, _Value({key: value}))

        # Determine cast method
        if callable(cast):
            cast = cast
            cast_from.append(f"cast_is_callable")
        elif cast is None and (default is NOT_SET or default is None):
            cast = as_is
            cast_from.append(f"cast_is_none_and_no_defaults")
        elif isinstance(default, bool):
            cast = as_boolean
            cast_from.append(f"cast_as_boolean")
        elif cast is None:
            cast = type(default)
            cast_from.append(f"cast_is_none")
        elif cast is NOT_SET:
            if default is NOT_SET or default is None:
                cast_from.append(f"cast_notset_type_default")
                cast = type(default)
            else:
                cast_from.append(f"cast_notset_type_as_is")
                cast = as_is
        else:
            raise TypeError(f"Cast must be callable, got: {type(cast)}")

        # Process things
        result = NOT_SET
        loader_from = []
        for loader in loaders:
            loader_from.append(str(loader))
            try:
                print(f"  > LOADER: try search in {loader} key: {key}")
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

        # Try to cast value
        error = None
        try:
            result = cast(result)
            results_from.append(f"casted:{cast}")
        # except ValueError as err:
        #     error = err
        except exceptions.InvalidCastConfiguration as err:
            error = err

        # Check for strict_cast mode:
        # print ("DEFAUUUB", conf_instance, conf_instance._strict_cast)
        if error is not None and conf_instance._strict_cast is True:
            msg = f"Got error {conf_instance}.{key} {type(error)}: {error}, set strict_cast=False to disable this error"
            raise exceptions.CastValueFailure(msg)

        meta = SimpleNamespace(
            cast=cast,
            default=default,
            loaders=loaders,
            value=result,
            cast_from=cast_from,
            loader_from=loader_from,
            results_from=results_from,
            default_from=default_from,
        )

        return result, meta


class FieldConf(Field):
    "Nested Config"

    def __init__(
        self,
        children_class,
        # children_class: NOT_SET = NOT_SET,
        key: str = None,
        **kwargs,
    ):

        super(FieldConf, self).__init__(key, **kwargs)
        self.children_class = children_class


class FieldBool(Field):
    "Boolean field"

    cast = as_boolean


class FieldString(Field):
    "String field"
    cast = str


class FieldInt(Field):
    "Int field"
    cast = as_int


class FieldFloat(Field):
    "Float field"
    cast = float


class FieldOption(Field):
    "Option field"
    cast = as_option

    def __init__(
        self,
        options,
        default_option=FAIL,
        key: str = None,
        **kwargs,
    ):

        assert isinstance(options, dict), f"Expected a dict, got: {options}"
        self.cast = AsOption(options, default_option=default_option)
        super(FieldOption, self).__init__(key, **kwargs)


# Children items
class FieldDict(Field):
    "Dict field"
    cast = as_dict


class FieldList(Field):
    "List field"
    cast = as_list


class FieldTuple(Field):
    "Tuple field"
    cast = as_tuple


# Compatibility with classyconf
Value = Field
