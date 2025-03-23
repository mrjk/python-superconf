"""Superconf - Python Configuration Library

This package provides a powerful configuration management system for Python applications.
It allows for hierarchical configuration, type validation, and flexible loading from
various sources.
"""

__version__ = "0.1.0"

# Import anchors
from superconf.lib.anchors import (
    ABS,
    ABSOLUTE,
    REL,
    RELATIVE,
    FileAnchor,
    PathAnchor,
)

# Import casts
from superconf.casts import (
    as_boolean,
    as_dict,
    as_int,
    as_is,
    as_list,
    as_option,
    as_tuple,
)

# Import common utilities and constants
from superconf.common import (
    FAIL,
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
)

# Import key classes from configuration module
from superconf.configuration import (
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
    Leaf,
)

# Import exceptions
from superconf.exceptions import (
    CastValueFailure,
    ConfigurationException,
    InvalidCastConfiguration,
    InvalidConfigurationFile,
    InvalidField,
    InvalidPath,
    MissingSettingsSection,
    UndeclaredField,
    UnknownChild,
    UnknownExtraField,
    UnknownSetting,
)

# Import field types from fields module
from superconf.fields import (
    Field,
    FieldBool,
    FieldConf,
    FieldContainer,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldLeaf,
    FieldList,
    FieldOption,
    FieldString,
    FieldTuple,
)
