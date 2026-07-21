"""Configuration data sources: format converters to/from nested dicts.

Sources load and dump nested dictionaries. They do not decide precedence;
that is the role of ``superconf.views.View``.
"""

from superconf.sources.base import (
    BaseSource,
    DataDict,
    DataFactory,
    SourceDumpError,
    SourceError,
    SourceLoadError,
    TextFileSource,
    resolve_mapping,
)
from superconf.sources.config import ConfigSource
from superconf.sources.dict import DictSource
from superconf.sources.env import EnvSource
from superconf.sources.json import JsonSource
from superconf.sources.toml import TomlSource
from superconf.sources.yml import YamlSource

__all__ = [
    "BaseSource",
    "ConfigSource",
    "DataDict",
    "DataFactory",
    "DictSource",
    "EnvSource",
    "JsonSource",
    "SourceDumpError",
    "SourceError",
    "SourceLoadError",
    "TextFileSource",
    "TomlSource",
    "YamlSource",
    "resolve_mapping",
]
