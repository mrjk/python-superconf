

from pprint import pprint
import json
from dataclasses import dataclass




# ================================================
# Base datasets
# ================================================


@dataclass
class DataSet:
    """Class that store a test dataset."""
    name: str = None
    desc: str = None
    value: type(None) = None


# Base values
store_value_base = {
    "val_none": DataSet(
        desc = "None value",
        value = None,
    ),


    "val_string": DataSet(
        desc = "String value",
        value = "string_value",
    ),


    "val_bool_true": DataSet(
        desc = "Boolean True value",
        value = True,
    ),
    "val_bool_true": DataSet(
        desc = "Boolean False value",
        value = False,
    ),


    "val_int": DataSet(
        desc = "Int 0 value",
        value = 0,
    ),
    "val_int_42": DataSet(
        desc = "Int 42 value",
        value = 42,
    ),
    "val_int__51": DataSet(
        desc = "Int -51 value",
        value = -51,
    ),


    "val_dict_empty": DataSet(
        desc = "Dict empty",
        value = {},
    ),
    "val_list_empty": DataSet(
        desc = "List empty",
        value = [],
    ),

}

# Base dict
store_dict_base = {

    "dict_flat_empty": DataSet(
        desc = "Empty dict()",
        value = {},
    ),
    "dict_flat_none": DataSet(
        desc = "Dictionnary with 3 keys and none values",
        value = {
            "dict_key1": None,
            "dict_key2": None,
            "dict_key3": None,
        }
    ),
    "dict_flat_string": DataSet(
        desc = "Dictionnary with 3 keys and string values",
        value = {
            "dict_key1": "dict_string_val1",
            "dict_key2": "dict_string_val2",
            "dict_key3": "dict_string_val3",
        }
    ),
    "dict_flat_string_unset": DataSet(
        desc = "Dictionnary with 3 keys and none&string values",
        value = {
            "key1": "dict_string_val1",
            "key2": None,
            "key3": None,
        }
    ),
    "dict_flat_mixed": DataSet(
        desc = "Dictionnary with 5 keys and with mixed null type values",
        value = { key: val.value for key, val in store_value_base.items()}
    ),

}

# Base list
store_list_base = {

    "list_flat_empty": DataSet(
        desc = "Empty list()",
        value = list(),
    ),
    "list_flat_none": DataSet(
        desc = "List with 3 none values",
        value = [
            None,
            None,
            None,
        ]
    ),
    "list_flat_string": DataSet(
        desc = "List with 3 keys and string values",
        value = {
            "list_string_val1",
            "list_string_val2",
            "list_string_val3",
        }
    ),
    "list_flat_string_unset": DataSet(
        desc = "List with 3 keys and none&string values",
        value = {
            "list_string_val1",
            None,
            None,
        }
    ),
    "list_flat_mixed": DataSet(
        desc = "List with all keys and with mixed null type values",
        value = [val.value for key, val in store_value_base.items()]
    ),

}

