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

# Import common
# from tests.common import store_value_base, store_dict_base, store_list_base
# from tests.common import report_node_values
# from tests.common import types_base


from superconf.node import NodeBase, NodeContainer, NodeMeta, NodeChildren
from superconf.node import UNSET, DEFAULT_VALUE, UNSET_VALUE
import superconf.exceptions


# ================================================
# Base datasets
# ================================================

CLS_TEST = [NodeBase, NodeContainer, NodeMeta, NodeChildren]
# CLS_TEST = [NodeBase, NodeContainer]


def report_node_values(inst, **kwargs):
    "Aggreagate values to watch/test"

    result = {
        "type": type(inst),
        "name": inst.name,
        "namef": inst.fname,
        "get_parents_count": len(inst.get_parents(mode="parents")),
        "get_parents()": len(inst.get_parents(mode="parents")),
    }
    if kwargs:
        result["____CONTEXT"] = kwargs
    return result


# ================================================
# Base tests on classes
# ================================================


@pytest.mark.parametrize("cls", CLS_TEST)
def test_node_init(fx_store_value_base, data_regression, cls):
    "Test a default Node"

    test_results = {}

    try:
        inst = cls()

        # Build regression report
        test_results = report_node_values(inst, cls=cls)

    except Exception as err:
        test_results = {"exception": str(type(err))}
        assert False, "No exception should happen"

    # assert False
    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


@pytest.mark.parametrize("cls", CLS_TEST)
def test_node_name(fx_store_value_base, data_regression, cls):
    "Test a default Storevalue"

    test_results = {}
    for key, val in fx_store_value_base.items():

        try:
            inst = cls(name=val.value)

            # Build regression report
            result = report_node_values(inst, cls=cls, default=val.value)

        except Exception as err:
            result = {"exception": str(type(err))}

            if isinstance(val.value, str):
                assert False, "No exception should happen on strings types"

        test_results[key] = result

    # assert False
    test_results = json.loads(to_json(test_results))
    data_regression.check(test_results)


# ================================================
# Complex datasets
# ================================================
