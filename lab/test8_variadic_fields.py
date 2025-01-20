# pylint: skip-file


import sys
from pprint import pprint

import pytest

import superconf.exceptions
from superconf.common import DEFAULT, FAIL, NOT_SET
from superconf.configuration import (
    Configuration,
    ConfigurationDict,
    Environment,
)
from superconf.fields import (

    Field,
    FieldBool,
    FieldConf,
    FieldDict,
    FieldFloat,
    FieldInt,
    FieldList,
    FieldOption,
    FieldString,
    FieldTuple,
)
from superconf.loaders import Dict

# This test explore the nested use cases, WITH defaults
