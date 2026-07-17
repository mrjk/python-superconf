---
jupyter:
  jupytext:
    cell_metadata_filter: -all
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.19.4
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

# Behavior Customization with Meta and Casting

Welcome to the fifth SuperConf tutorial! In this guide, we'll explore advanced customization options for configuring your SuperConf models using the `Meta` class and custom casting functionality.

As your applications grow in complexity, you'll often need to customize how your configuration classes behave. For example, you might want to:

- Allow extra fields that weren't explicitly defined in your class
- Set default values for the entire configuration
- Apply custom type conversion to your fields
- Customize how child nodes are created in container fields

SuperConf provides powerful mechanisms for all of these customizations through the `Meta` class and custom casting.

## Understanding the Meta Class

The `Meta` class is a special inner class used to configure behavior for configuration classes. It's a common pattern in many Python libraries (like Django's model Meta) for providing class-level configuration.

In SuperConf, the `Meta` class lets you define settings that control how configuration objects behave without cluttering the main class definition.

Key `Meta` settings include:

- `extra_fields`: Allow fields that weren't explicitly defined in the class
- `default`: Default values for the entire configuration 
- `cast`: Custom casting function for the entire configuration
- `children_class`: Default class for child nodes
- `merge`: How this node combines with another via `merge()` (see [106_merge_policies.md](106_merge_policies.md))

Let's explore each of these options in detail.

## Customizing Configuration Behavior with Meta

Let's start by creating a configuration class with a `Meta` inner class:

```python
from superconf import ConfigurationObj
from superconf.fields import Field, FieldString, FieldInt

class AppConfig(ConfigurationObj):
    """Application configuration with customized behavior"""
    
    class Meta:
        # Allow extra fields that weren't defined in the class
        extra_fields = True
        
        # Default values for the entire configuration
        default = {
            "app_name": "DefaultApp",
            "timeout": 30,
            "extra_setting": "This wasn't explicitly defined",
        }
    
    # Explicitly defined fields
    app_name = FieldString(help="Application name")
    timeout = FieldInt(help="Timeout in seconds")

# Create an instance with default values
app = AppConfig()

# Print the configuration values
print("Configuration with Meta defaults:")
print(f"app_name: {app.app_name}")
print(f"timeout: {app.timeout}")
print(f"extra_setting: {app.extra_setting}")  # This field is from Meta.default

# Verify values match the defaults
assert app.app_name == "DefaultApp"
assert app.timeout == 30
assert app.extra_setting == "This wasn't explicitly defined"
```

Notice that we can access `extra_setting` even though it wasn't explicitly defined as a field in the class. This is because we set `extra_fields = True` in the `Meta` class.

### Working with Extra Fields

When `extra_fields` is `True`, the configuration can accept keys that weren't explicitly defined as fields in the class. This is useful when you want to be flexible about what settings your configuration can handle:

```python
# Create a configuration with an extra field
config_data = {
    "app_name": "MyApp",
    "timeout": 60,
    "custom_setting": "Custom value",  # Not defined in the class
}

app = AppConfig(value=config_data)

# Print all configuration values
print("\nConfiguration with extra fields:")
print(f"app_name: {app.app_name}")
print(f"timeout: {app.timeout}")
print(f"custom_setting: {app.custom_setting}")  # This was not defined as a field

# Verify values were set correctly
assert app.app_name == "MyApp"
assert app.timeout == 60
assert app.custom_setting == "Custom value"

# Add another extra field dynamically
app.another_setting = "Added later"
print(f"another_setting: {app.another_setting}")

# Try to list all fields
print("\nAll fields in the configuration:")
for name, field in app.items():
    print(f"  {name}: {field.get_value()}")
```

Without `extra_fields = True`, trying to set or access undefined fields would raise an error.

### Default Values in Meta

The `default` setting in `Meta` provides default values for the entire configuration. This is especially useful when you have a complex configuration structure with many fields:

```python
# Create a different configuration class with only Meta.default
class SimpleConfig(ConfigurationObj):
    class Meta:
        default = {
            "setting1": "value1, from meta.default",
            "setting2": "value2, from meta.default",
        }

    setting1 = FieldString()
    setting2 = FieldString(default="value2, not taken in account since in meta.default")
    setting3 = FieldString()
    setting4 = FieldString(default="value4, from field.default")

# Create an instance with no explicit fields
simple = SimpleConfig()

# Print the default values
print("\nSimple configuration with only Meta.default:")
print(f"setting1: {simple.setting1}")
print(f"setting2: {simple.setting2}")
print(f"setting3: {simple.setting3}")
print(f"setting4: {simple.setting4}")

# Create an instance with some overrides
simple_custom = SimpleConfig(value={"setting2": "custom2", "setting3": "custom3"})

# Print the merged values
print("\nSimple configuration with some overrides:")
print(f"setting1: {simple_custom.setting1}")  # From default
print(f"setting2: {simple_custom.setting2}")  # Overridden
print(f"setting3: {simple_custom.setting3}")  # From default
print(f"setting4: {simple_custom.setting4}")  # From default
```

## Custom Casting

Casting is the process of converting raw values to the appropriate types. SuperConf provides built-in casting for various field types, but you can also define custom casting behavior for more complex scenarios.

### Understanding How Casting Works

When you set a value to a field, SuperConf applies the field's cast function to convert the value to the appropriate type. For example, `FieldInt` casts values to integers.

Let's first see how the built-in casting works:

```python
from superconf.fields import FieldInt, FieldString, FieldBool

# Create a simple configuration to demonstrate built-in casting
class TypedConfig(ConfigurationObj):
    int_field = FieldInt(default="42")  # String will be cast to int
    string_field = FieldString(default=123)  # Number will be cast to string
    bool_field = FieldBool(default="yes")  # String will be cast to boolean

# Create an instance
typed = TypedConfig()

# Print the casted values
print("\nBuilt-in casting examples:")
print(f"int_field: {typed.int_field} (type: {type(typed.int_field).__name__})")
print(f"string_field: {typed.string_field} (type: {type(typed.string_field).__name__})")
print(f"bool_field: {typed.bool_field} (type: {type(typed.bool_field).__name__})")

# Verify the types
assert isinstance(typed.int_field, int)
assert isinstance(typed.string_field, str)
assert isinstance(typed.bool_field, bool)
```

### Creating a Custom Cast Class

For more complex casting needs, you can create your own cast logic function:

```python
def email_cast(value):
    """Convert value to a valid email format"""
    if value is None:
        return None
        
    value = str(value).strip().lower()
    
    # Simple validation
    if "@" not in value:
        value = f"{value}@example.com"
        
    return value

# Print what happens with different inputs
print("\nCustom email casting examples:")
print(f"'user': {email_cast('user')}")
print(f"'USER': {email_cast('USER')}")
print(f"'user@company.com': {email_cast('user@company.com')}")
print(f"None: {email_cast(None)}")
print(f"123: {email_cast(123)}")
```

But internally, this is implemented as a class. A cast class is any callable that takes a value and returns a converted value.

Let's create a custom cast for email addresses:

```python
from superconf.casts import AbstractCast

class EmailCast(AbstractCast):
    """Cast for email addresses"""
    
    def __call__(self, value):
        """Convert value to a valid email format"""
        if value is None:
            return None
            
        value = str(value).strip().lower()
        
        # Simple validation
        if "@" not in value:
            value = f"{value}@example.com"
            
        return value

# Print what happens with different inputs
email_cast = EmailCast()
print("\nCustom email casting examples:")
print(f"'user': {email_cast('user')}")
print(f"'USER': {email_cast('USER')}")
print(f"'user@company.com': {email_cast('user@company.com')}")
print(f"None: {email_cast(None)}")
print(f"123: {email_cast(123)}")
```

### Using a Custom Cast with Fields

Now let's use our custom email cast in a configuration field:

```python
# Create a configuration class with custom email casting
class UserConfig(ConfigurationObj):
    """User configuration with custom email casting"""
    
    # Field with custom cast
    email = Field(default="admin", cast=email_cast)
    
    # Other fields
    name = Field(default="User")

# Create a configuration
user = UserConfig()

# Print the values
print("\nUser configuration with custom email casting:")
print(f"email: {user.email}")
print(f"name: {user.name}")

# Verify the default value is casted
assert user.email == "admin@example.com"

# Set new values and see how they're casted
print("\nSetting new values:")
user.email = "support"
print(f"After setting 'support': {user.email}")
assert user.email == "support@example.com"

user.email = "contact@company.com"
print(f"After setting 'contact@company.com': {user.email}")
assert user.email == "contact@company.com"
```

## Children Classes for Containers

The `children_class` attribute in `Meta` defines what class should be used for dynamically created children. This is particularly useful for variadic collections like `ConfigurationDict`:

```python
from superconf import ConfigurationObj, ConfigurationDict
from superconf.fields import FieldString

class ResourceItem(ConfigurationObj):
    """Configuration for a single resource"""
    name = FieldString(default="Unnamed")
    type = FieldString(default="generic")

class ResourcesDict(ConfigurationDict):
    """Dictionary of resources with custom children class"""
    
    class Meta:
        # All dynamically created children will be ResourceItem instances
        children_class = ResourceItem

# Create a configuration with dynamic children
resources = ResourcesDict(value={
    "res1": {"name": "Database", "type": "postgres"},
    "res2": {"name": "Cache", "type": "redis"},
})

# Print the resources
print("\nResources with custom children class:")
for key, resource in resources.items():
    print(f"Resource {key}:")
    print(f"  Name: {resource['name']}")
    print(f"  Type: {resource.type}")
    print(f"  Class: {type(resource).__name__}")

# Print the resources
print("\nResources with custom children class:")
for key, resource in resources.items():
    print(f"Resource {key}:")
    print(f"  Name: {resource['name']}")
    print(f"  Type: {resource.type}")
    print(f"  Class: {type(resource).__name__}")

# Each child is a ResourceItem instance
assert isinstance(resources.res1, ResourceItem)
assert resources.res1.name == "Database"
assert resources.res1.type == "postgres"
```

## Combining Meta Settings

You can combine multiple `Meta` settings for sophisticated behavior. Let's create a feature flag configuration with boolean casting and default values:

```python
from superconf import ConfigurationObj, ConfigurationDict, Field, FieldBool, FieldConf, as_boolean

class FeatureFlags(ConfigurationObj):
    """Dynamic feature flag configuration"""
    
    class Meta:
        # Default features
        default = {
            "dark_mode": False,
            "beta_features": False,
            "analytics": True,
        }

    dark_mode = FieldBool(default=True)
    beta_features = FieldBool(default=False)
    analytics = FieldBool(default=True)

class AppConfig(ConfigurationObj):
    """Main app configuration with feature flags"""
    
    class Meta:
        # Global application defaults
        default = {
            "app_name": "FeatureApp",
            "features": {
                "dark_mode": True,
                "analytics": False,
            }
        }
    
    # Basic fields
    app_name = Field(default="DefaultApp")
    
    # Feature flags container
    features = FieldConf(FeatureFlags)

# Create a configuration
app = AppConfig()

# Print the configuration
print("\nApplication with feature flags:")
print(f"app_name: {app.app_name}")

# Print the feature flags
print("\nFeature flags:")
for name, enabled in app.features.items():
    print(f"  {name}: {enabled}")

# Verify feature flags
assert app.features.dark_mode is True
assert app.features.beta_features is False
assert app.features.analytics is False
```

## Practical Example: Web Application Configuration

Let's put everything together in a practical example - a web application configuration with custom casting, defaults, and extra fields:

```python
from superconf import ConfigurationObj, ConfigurationDict
from superconf.fields import Field, FieldConf, FieldInt, FieldString, FieldBool

# Custom cast for URL normalization
class UrlCast:
    def __call__(self, value):
        if not value:
            return ""
        
        value = str(value).strip()
        
        # Add https:// if no protocol specified
        if "://" not in value:
            value = f"https://{value}"
            
        # Ensure trailing slash
        if not value.endswith("/"):
            value += "/"
            
        return value

# Cast for port number validation
class PortCast:
    def __call__(self, value):
        port = int(value)
        if port < 1 or port > 65535:
            raise ValueError(f"Invalid port number: {port}")
        return port

# Database configuration
class DatabaseConfig(ConfigurationObj):
    host = FieldString(default="localhost")
    port = Field(default=5432, cast=PortCast())
    name = FieldString(default="app")
    user = FieldString(default="postgres")
    password = FieldString(default="")

# API endpoint configuration
class ApiEndpoint(ConfigurationObj):
    url = Field(default="", cast=UrlCast())
    timeout = FieldInt(default=30)
    retries = FieldInt(default=3)

# API endpoints dictionary
class ApiEndpoints(ConfigurationDict):
    class Meta:
        children_class = ApiEndpoint
        default = {
            "users": {"url": "api.example.com/users"},
            "products": {"url": "api.example.com/products"},
        }

# Main web application configuration
class WebAppConfig(ConfigurationObj):
    class Meta:
        extra_fields = True
        default = {
            "app_name": "WebApp",
            "debug": False,
            "host": "localhost",
            "port": 8080,
            "log_level": "info",
        }
    
    app_name = FieldString(help="Application name")
    debug = FieldBool(help="Enable debug mode")
    host = FieldString(help="Server hostname")
    port = Field(cast=PortCast(), help="Server port")
    
    # Nested configurations
    database = FieldConf(DatabaseConfig, help="Database configuration")
    api = FieldConf(ApiEndpoints, help="API endpoints")

# Create the configuration
webapp = WebAppConfig()

# Print the configuration
print("\n\nWeb Application Configuration:")
print(f"app_name: {webapp.app_name}")
print(f"debug: {webapp.debug}")
print(f"host: {webapp.host}")
print(f"port: {webapp.port}")
print(f"log_level: {webapp.log_level}")  # Extra field from Meta.default

print("\nDatabase Configuration:")
print(f"host: {webapp.database.host}")
print(f"port: {webapp.database.port}")
print(f"name: {webapp.database.name}")
print(f"user: {webapp.database.user}")

print("\nAPI Endpoints:")
for name, endpoint in webapp.api.items():
    print(f"  {name}: {endpoint.url} (timeout: {endpoint.timeout}s, retries: {endpoint.retries})")

# Create a configuration with custom values
custom_config = {
    "app_name": "MyWebApp",
    "debug": True,
    "port": 9000,
    "theme": "dark",  # Extra field
    "database": {
        "host": "db.example.com",
        "name": "myapp",
    },
    "api": {
        "users": {"timeout": 10},
        "orders": {"url": "api.example.com/orders"},  # New endpoint
    }
}

webapp = WebAppConfig(value=custom_config)

# Print the customized configuration
print("\nCustomized Web Application Configuration:")
print(f"app_name: {webapp.app_name}")
print(f"debug: {webapp.debug}")
print(f"host: {webapp.host}")
print(f"port: {webapp.port}")
print(f"theme: {webapp.theme}")  # Extra field

print("\nDatabase Configuration:")
print(f"host: {webapp.database.host}")
print(f"port: {webapp.database.port}")
print(f"name: {webapp.database.name}")
print(f"user: {webapp.database.user}")

print("\nAPI Endpoints:")
for name, endpoint in webapp.api.items():
    print(f"  {name}: {endpoint.url} (timeout: {endpoint.timeout}s, retries: {endpoint.retries})")
```

## Summary

In this guide, we've learned:

- How to use the `Meta` class to customize configuration behavior
- How to allow extra fields in a configuration
- How to define default values at the class level
- How to create and use custom cast functions
- How to set global casts for all fields
- How to define default child classes for containers
- How to combine multiple Meta settings for sophisticated behavior
- How to apply these concepts in a practical web application configuration

These advanced features allow you to fine-tune SuperConf's behavior to match your specific requirements, making it a powerful and flexible configuration management solution.

## Next guide

Merge trees with policies: [106_merge_policies.md](106_merge_policies.md).

## Try It Yourself

Here are some exercises to practice what you've learned:

1. Create a configuration for a web application with custom casting for URLs and ports
2. Implement a custom cast that validates email addresses with a regex pattern
3. Create a configuration with extra fields and experiment with adding fields dynamically
4. Define a configuration with default values in Meta and override some values
5. Combine multiple Meta settings (cast, default, extra_fields) in a single configuration
6. Create a nested configuration with custom casting at multiple levels 

```python

```
