"""Superconf - Python Configuration Library

This package provides a powerful configuration management system for Python applications.
It allows for hierarchical configuration, type validation, and flexible loading from
various sources.
"""

__version__ = "0.1.4"

# Import casts
from superconf.casts import (  # as_option,
    as_boolean,
    as_dict,
    as_int,
    as_is,
    as_list,
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
from superconf.fields import (  # FieldOption,
    Field,
    FieldBool,
    FieldConf,
    FieldContainer,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldLeaf,
    FieldList,
    FieldString,
    FieldTuple,
)

# Import anchors
from superconf.lib.anchors import (
    ABS,
    ABSOLUTE,
    REL,
    RELATIVE,
    FileAnchor,
    PathAnchor,
)
