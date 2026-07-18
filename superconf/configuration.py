"""Compatibility imports for the legacy configuration module."""

from superconf import exceptions
from superconf.casts import as_dict, as_is, as_list
from superconf.common import (
    MERGE_DICT_DEFAULT,
    MERGE_LIST_DEFAULT,
    MERGE_OTHER_DEFAULT,
    NOT_SET,
    NOT_SET_DICT,
    NOT_SET_LIST,
    UNSET_ARG,
    infer_merge_kind,
    is_merge_value_set,
    merge_data,
    merge_maps,
    normalize_merge_strategy,
    prefer_other_scalar,
    truncate,
    unique,
)
from superconf.container import (
    ConfigurationDict,
    ConfigurationList,
    ConfigurationObj,
    DeclarativeValuesMetaclass,
    _ContainerInstance,
)
from superconf.leaf import (
    GenericField,
    Leaf,
    LeafBaseConfig,
    LeafContainerConfig,
    LeafObjConfig,
    PublicField,
    node_cast_value,
)
from superconf.merge import MergeKind
from superconf.nodes import Node

Configuration = ConfigurationObj

__all__ = [
    "Configuration",
    "ConfigurationDict",
    "ConfigurationList",
    "ConfigurationObj",
    "DeclarativeValuesMetaclass",
    "GenericField",
    "Leaf",
    "LeafBaseConfig",
    "LeafContainerConfig",
    "LeafObjConfig",
    "MERGE_DICT_DEFAULT",
    "MERGE_LIST_DEFAULT",
    "MERGE_OTHER_DEFAULT",
    "MergeKind",
    "NOT_SET",
    "NOT_SET_DICT",
    "NOT_SET_LIST",
    "Node",
    "PublicField",
    "UNSET_ARG",
    "_ContainerInstance",
    "as_dict",
    "as_is",
    "as_list",
    "exceptions",
    "infer_merge_kind",
    "is_merge_value_set",
    "merge_data",
    "merge_maps",
    "node_cast_value",
    "normalize_merge_strategy",
    "prefer_other_scalar",
    "truncate",
    "unique",
]
