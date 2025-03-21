"""Superconf - Python Configuration Library

This package provides a powerful configuration management system for Python applications.
It allows for hierarchical configuration, type validation, and flexible loading from
various sources.
"""

__version__ = "0.1.0"

# Import key classes from configuration module
from superconf.configuration import (
    Leaf,
    ConfigurationObj,
    ConfigurationDict,
    ConfigurationList,
)

# Import field types from fields module
from superconf.fields import (
    Field,
    FieldLeaf,
    FieldContainer,
    FieldBool,
    FieldString,
    FieldInt,
    FieldFloat,
    FieldOption,
    FieldDict,
    FieldList,
    FieldTuple,
    FieldConf,
)

# Import exceptions
from superconf.exceptions import (
    ConfigurationException,
    InvalidConfigurationFile,
    MissingSettingsSection,
    InvalidPath,
    InvalidCastConfiguration,
    CastValueFailure,
    UndeclaredField,
    UnknownExtraField,
    UnknownSetting,
    UnknownChild,
    InvalidField,
)

# Import casts
from superconf.casts import (
    as_is,
    as_boolean,
    as_int,
    as_dict,
    as_list,
    as_tuple,
    as_option,
)

# Import common utilities and constants
from superconf.common import (
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    FAIL,
)

# Import anchors
from superconf.anchors import (
    PathAnchor,
    FileAnchor,
    RELATIVE,
    ABSOLUTE,
    REL,
    ABS,
) 