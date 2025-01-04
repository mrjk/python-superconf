import pytest
import inspect
from logging import Logger
from pprint import pprint
import json
from dataclasses import dataclass


from superconf.store import UNSET, DEFAULT_VALUE, UNSET_VALUE
from superconf.store import StoreValue, StoreDict, StoreList, StoreConf
from superconf.store import StoreAny, StoreAuto
from superconf.store import Value, ValueConf, ValueDict, ValueList

from superconf.store import store_to_json

import superconf.exceptions as exceptions
from superconf.common import to_json

from tests.common import store_value_base, store_dict_base, store_list_base
from tests.common import report_store_values

# from tests.common import types_base


# ================================================
# Datasets
# ================================================


CLS_STORE_TESTS = [StoreValue, StoreDict, StoreList, StoreConf, StoreAny, StoreAuto]

CLS_VALUE_TESTS = [Value, ValueConf, ValueDict, ValueList]

CLS_TEST = CLS_STORE_TESTS + CLS_VALUE_TESTS


# ================================================
# Base tests on classes
# ================================================


@pytest.mark.parametrize("cls", CLS_TEST)
def test_cls_direct_instance(data_regression, cls):
    "Test each classes directly without arguments"

    test_results = {}
    try:
        inst = cls()
        test_results = report_store_values(inst, cls=cls)

    except Exception as err:
        test_results = {"exception": str(type(err))}

    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


@pytest.mark.parametrize("cls", CLS_TEST)
def test_cls_with_arg_value(types_base, data_regression, cls):
    "Test each classes with argument value"

    test_results = {}
    for key, val in types_base.items():

        try:
            inst = cls(value=val.value)
            result = report_store_values(inst, cls=cls, value=val.value)

        except Exception as err:
            result = {"exception": str(type(err))}

        test_results[key] = result

    # assert False
    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


@pytest.mark.parametrize("cls", CLS_TEST)
def test_cls_with_arg_default(types_base, data_regression, cls):
    "Test each classes with argument default"

    test_results = {}
    for key, val in types_base.items():

        try:
            inst = cls(default=val.value)
            result = report_store_values(inst, cls=cls, default=val.value)

        except Exception as err:
            result = {"exception": str(type(err))}

        test_results[key] = result

    # assert False
    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


@pytest.mark.parametrize("cls", CLS_TEST)
def test_cls_with_arg_value_and_default(types_base, data_regression, cls):
    "Test each classes with value and default arguments"

    test_results = {}
    for key, val in types_base.items():

        try:
            inst = cls(value=val.value, default=val.value)
            result = report_store_values(
                inst, cls=cls, value=val.value, default=val.value
            )

        except Exception as err:
            result = {"exception": str(type(err))}

        test_results[key] = result

    # assert False
    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


# ================================================
# Complex datasets
# ================================================
