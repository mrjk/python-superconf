
import pytest


from tests.common import store_value_base, store_dict_base, store_list_base



# Prepare large datasets
@pytest.fixture
def types_base():

    dataset = dict()
    dataset.update(store_value_base)
    dataset.update(store_dict_base)
    dataset.update(store_list_base)

    return dataset


# Prepare large datasets
@pytest.fixture
def fx_store_value_base():

    dataset = dict()
    dataset.update(store_value_base)
    # dataset.update(store_dict_base)
    # dataset.update(store_list_base)

    return dataset

@pytest.fixture
def fx_store_value_dict():

    dataset = dict()
    # dataset.update(store_value_base)
    dataset.update(store_dict_base)
    # dataset.update(store_list_base)

    return dataset

@pytest.fixture
def fx_store_value_list():

    dataset = dict()
    # dataset.update(store_value_base)
    # dataset.update(store_dict_base)
    dataset.update(store_list_base)

    return dataset



