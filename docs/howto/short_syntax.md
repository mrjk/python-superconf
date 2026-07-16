# Short syntax for nested dict containers

When you only need a `ConfigurationDict` of a known child type, you can skip declaring an intermediate subclass.

## Long form

```python
from superconf import ConfigurationDict, ConfigurationObj, FieldConf, FieldString

class AppFeature(ConfigurationObj):
    name = FieldString()
    group = FieldString(default="__base__")

class AppFeatures(ConfigurationDict):
    class Meta:
        children_class = AppFeature

class App(ConfigurationObj):
    features = FieldConf(AppFeatures)
```

## Short form

Pass `ConfigurationDict` to `FieldConf` and set `children_class` there:

```python
from superconf import ConfigurationDict, ConfigurationObj, FieldConf, FieldString

class AppFeature(ConfigurationObj):
    class Meta:
        extra_fields = True

    name = FieldString(help="Feature name")
    group = FieldString(default="__base__", help="Default group")

class App(ConfigurationObj):
    features = FieldConf(
        ConfigurationDict,
        help="Feature map",
        children_class=AppFeature,
    )

app = App(value={
    "features": {
        "feat1": {"name": "feat1", "group": "group1"},
        "feat2": {"name": "feat2", "extra": True},
    }
})

assert app.features.feat1.group == "group1"
assert app.features.feat2.extra is True
```

## Pitfall

`extra_fields` is a `ConfigurationObj` Meta option. Passing it as a `FieldConf(ConfigurationDict, extra_fields=True)` kwarg raises `InvalidFieldOption`. Put `extra_fields` on the child class instead.
