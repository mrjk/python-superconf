"""Meta defaults and extra_fields for undeclared keys."""

from pprint import pprint

from superconf import NOT_SET, ConfigurationObj, Field, UndeclaredField


class StrictConfig(ConfigurationObj):
    """Rejects Meta.default keys that are not declared fields."""

    class Meta:
        default = {
            "name": "from-meta",
            "extra": "not allowed",
        }
        extra_fields = False

    name = Field(default="declared")


class OpenConfig(ConfigurationObj):
    """Allows Meta.default keys beyond declared fields."""

    class Meta:
        default = {
            "name": "from-meta",
            "extra": "allowed",
        }
        extra_fields = True

    name = Field()
    note = Field()


# Strict: undeclared Meta.default key fails
try:
    StrictConfig()
except UndeclaredField:
    print("StrictConfig correctly rejected undeclared Meta.default key")
else:
    raise AssertionError("expected UndeclaredField")


open_cfg = OpenConfig()
print("\nOpenConfig with extra_fields:")
pprint(open_cfg.get_value())

assert open_cfg.name == "from-meta"
assert open_cfg.get_value("extra") == "allowed"
assert open_cfg.note is NOT_SET

# Runtime payload can also carry extra keys when allowed
open_cfg.set_value({"name": "runtime", "extra": "updated", "another": 1})
print("\nAfter set_value with extras:")
pprint(open_cfg.get_value())
assert open_cfg.name == "runtime"
assert open_cfg.get_value("another") == 1

print("\nOK")
