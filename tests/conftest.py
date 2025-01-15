import pytest
from superconf.configuration import Configuration, ConfigurationDict, Field, FieldConf, Environment
from superconf.fields import FieldBool, FieldInt, FieldString, FieldDict, FieldList
from superconf.loaders import Dict

# Sample test data
EXAMPLE_DICT = {
    "item1": True,
    "item2": 4333,
}

FULL_CONFIG = {
    "field1": False,
    "field2": "Default value",
    "field3": 42,
    "field4": EXAMPLE_DICT,
}

NESTED_CONFIG = {
    "name": "MyApp",
    "version": "1.0.0",
    "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
            "username": "admin",
            "password": "secret"
        }
    },
    "features": ["auth", "api", "admin"]
}

@pytest.fixture
def basic_config_class():
    """A basic configuration class for testing"""
    class BasicConfig(Configuration):
        class Meta:
            loaders = [Environment()]
            cache = True

        field1 = Field(default=False, help="Toggle debugging")
        field2 = Field(default="Default value", help="String field")
        field3 = Field(default=42, help="Integer field")
        field4 = Field(default=EXAMPLE_DICT, help="Dict field")

    return BasicConfig

@pytest.fixture
def typed_config_class():
    """Configuration class with specific field types"""
    class TypedConfig(Configuration):
        class Meta:
            loaders = [Environment()]
            strict_cast = True

        debug = FieldBool(default=False, help="Debug mode")
        port = FieldInt(default=8080, help="Server port")
        name = FieldString(default="app", help="Application name")
        settings = FieldDict(default={}, help="Additional settings")
        plugins = FieldList(default=[], help="Enabled plugins")

    return TypedConfig

@pytest.fixture
def nested_config_class():
    """Configuration class with nested configuration"""
    class DatabaseConfig(Configuration):
        class Meta:
            extra_fields = True
        
        host = Field(default="localhost", help="Database host")
        port = FieldInt(default=5432, help="Database port")
        
    class AppConfig(Configuration):
        class Meta:
            loaders = [Dict(NESTED_CONFIG)]
        
        name = Field(default="app", help="App name")
        version = Field(default="0.1.0", help="App version")
        database = FieldConf(DatabaseConfig, help="Database configuration")
        features = FieldList(default=[], help="Enabled features")

    return AppConfig

@pytest.fixture
def config_with_dict_loader(basic_config_class):
    """Configuration instance with Dict loader"""
    return basic_config_class(loaders=[Dict(FULL_CONFIG)])

@pytest.fixture
def empty_config(basic_config_class):
    """Configuration instance with no data"""
    return basic_config_class()

@pytest.fixture
def typed_config(typed_config_class):
    """Instance of TypedConfig"""
    return typed_config_class()

@pytest.fixture
def nested_config(nested_config_class):
    """Instance of nested configuration"""
    return nested_config_class() 