import logging
from collections import OrderedDict
from typing import Callable

from pprint import pprint

from .loaders import NOT_SET, UNSET, UnSet, Environment
from .store import StoreValue, StoreConf, StoreDict, StoreList
from .store import Value, ValueConf, ValueDict, ValueList

log = logging.getLogger(__name__)



# ################################### Dev helpers


class DeclarativeValuesMetaclass(type):
    """
    Collect Value objects declared on the base classes
    """

    def __new__(self, class_name, bases, attrs):
        # Collect values from current class and all bases.
        values = OrderedDict()
        keys = []

        log = logging.getLogger(f"{class_name}")
        log.debug(f"{class_name}: Metaclass prepare")
        # Walk through the MRO and add values from base class.
        for base in reversed(bases):
            if hasattr(base, "_declared_values"):
                log.debug(f"{class_name}: Import values from parent class {base}")
                keys.extend(list(base._declared_values.keys()))
                values.update(base._declared_values)

        # Collet class values
        for key, value in attrs.items():
            if isinstance(value, Value):
                if value.key and key != value.key:
                    msg = "Don't explicitly set keys when declaring values"
                    log.warn(msg)
                    # raise AttributeError( msg )
                # key = value.key

                log.debug(f"{class_name}: Add value '{key}': {value}")
                value.key = key
                values.update({key: value})
                keys.append(key)

        keys = set(keys)
        for key in keys:
            attrs[key] = values[key]
        #     del values[key]
        attrs["_declared_values"] = values

        return super(DeclarativeValuesMetaclass, self).__new__(
            self, class_name, bases, attrs
        )

    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        # Remember the order that values are defined.
        return OrderedDict()


class _ConfigurationMixin:

    def __init__(self, *args, **kwargs):
        super(_ConfigurationMixin, self).__init__(*args, **kwargs)


## Instance Public


class Configuration(
    _ConfigurationMixin, StoreConf, metaclass=DeclarativeValuesMetaclass
):
    "Represent a known keys config"


class ConfigurationDict(
    _ConfigurationMixin, StoreDict, metaclass=DeclarativeValuesMetaclass
):
    "Represent a unknown keys config"


class ConfigurationList(
    _ConfigurationMixin, StoreList, metaclass=DeclarativeValuesMetaclass
):
    "Represent a unknown list config"
