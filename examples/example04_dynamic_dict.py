"""Dynamic dict of children via ConfigurationDict + children_class."""

from pprint import pprint

from superconf import ConfigurationDict, ConfigurationObj, Field, FieldConf


class Resource(ConfigurationObj):
    """One resource entry."""

    class Meta:
        extra_fields = True

    location = Field(default="MISSING LOCATION")
    owner = Field(default="MISSING OWNER")


class ResourcesDict(ConfigurationDict):
    """Map of named resources."""

    class Meta:
        children_class = Resource


class AppConfig(ConfigurationObj):
    """App holding a dynamic resource map."""

    resources = FieldConf(ResourcesDict)


payload = {
    "resources": {
        "laptop": {"location": "home", "owner": "rob"},
        "wifi-ap": {"location": "home", "owner": "michel"},
        "phone": {"location": "roaming", "owner": "rob"},
    }
}

app = AppConfig(value=payload)

print("Resources:")
pprint(app.resources.get_value())

assert isinstance(app.resources, ResourcesDict)
assert isinstance(app.resources.laptop, Resource)
assert app.resources.laptop.location == "home"
assert app.resources["wifi-ap"]["owner"] == "michel"
assert len(app.resources) == 3

print("\nPer-resource access:")
for key, resource in app.resources.items():
    print(f"  {key}: location={resource.location!r} owner={resource.owner!r}")

print("\nOK")
