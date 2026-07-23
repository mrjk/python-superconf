"""Nest ConfigurationObj children with FieldConf."""

from pprint import pprint

from superconf import ConfigurationObj, Field, FieldConf


class DbConfig(ConfigurationObj):
    """Nested database settings."""

    host = Field(default="localhost", help="Database host")
    port = Field(default=5432, help="Database port")
    name = Field(default="app", help="Database name")


class AppConfig(ConfigurationObj):
    """Top-level app with a nested child object."""

    app_name = Field(default="MyApp")
    debug = Field(default=False)
    database = FieldConf(DbConfig)


app = AppConfig()

print("Defaults (nested):")
pprint(app.get_value())

assert isinstance(app.database, DbConfig)
assert app.database.host == "localhost"
assert app.database.port == 5432
assert app("database") is app.database

# Override nested values
app = AppConfig(
    value={
        "app_name": "ProdApp",
        "debug": True,
        "database": {"host": "db.internal", "port": 5433},
    }
)

print("\nWith overrides:")
pprint(app.get_value())
assert app.app_name == "ProdApp"
assert app.database.host == "db.internal"
assert app.database.port == 5433
assert app.database.name == "app"  # still default

print("\nOK")
