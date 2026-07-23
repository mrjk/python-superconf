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
    MERGE_APPEND,
    MERGE_DICT_DEFAULT,
    MERGE_KEEP,
    MERGE_LIST_DEFAULT,
    MERGE_OTHER_DEFAULT,
    MERGE_OVERRIDE,
    MERGE_OVERRIDE_ABSENT,
    MERGE_OVERRIDE_NON_NULL,
    MERGE_OVERRIDE_PRESENT,
    MERGE_PREPEND,
    MERGE_REPLACE,
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    MergeKind,
    MergeStrategy,
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

# Multi-source views / converters (optional API)
from superconf.sources import (
    ConfigSource,
    DictSource,
    EnvSource,
    JsonSource,
    TomlSource,
    YamlSource,
)
from superconf.twelve_factor import (
    TwelveFactorError,
    build_12factor_view,
    from_12factor,
    load_12factor,
)
from superconf.views import TWELVE_FACTOR_ORDER, View
