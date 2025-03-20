# Hierarchical Configuration

This tutorial covers how to create hierarchical configurations in Superconf, allowing you to organize your configuration into structured, nested components.

## Nested Configuration

Superconf supports nested configuration structures using the `FieldConf` field type. This allows you to build complex configuration hierarchies that mirror your application's architecture.

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf
from superconf.configuration import ContainerConf

# Database configuration
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost", help="Database host")
    port = FieldInt(default=5432, help="Database port")
    name = FieldString(default="app_db", help="Database name")
    user = FieldString(help="Database user")
    password = FieldString(help="Database password")

# Cache configuration
class CacheConfig(ContainerConf):
    enabled = FieldBool(default=True, help="Enable caching")
    ttl = FieldInt(default=300, help="Cache TTL in seconds")
    backend = FieldString(default="memory", help="Cache backend")

# Application configuration with nested components
class AppConfig(ContainerConf):
    name = FieldString(default="MyApp", help="Application name")
    debug = FieldBool(default=False, help="Enable debug mode")
    
    # Nested configurations
    database = FieldConf(DatabaseConfig, help="Database configuration")
    cache = FieldConf(CacheConfig, help="Cache configuration")
```

With this structure, you can access nested configurations using attribute notation:

```python
# Create a configuration instance
config = AppConfig()

# Access nested configuration values
print(f"Database host: {config.database.host}")
print(f"Database port: {config.database.port}")
print(f"Cache enabled: {config.cache.enabled}")
print(f"Cache TTL: {config.cache.ttl}")
```

## Setting Nested Configuration Values

You can set values for nested configurations in several ways:

### During Initialization

You can provide nested values during initialization:

```python
# Using nested dictionaries
config = AppConfig(
    name="MyService",
    database={
        "host": "db.example.com",
        "port": 5433,
        "user": "admin",
        "password": "secret"  # Note: secrets are handled like a normal string
    },
    cache={
        "enabled": True,
        "ttl": 600
    }
)

# Or using nested configuration instances
db_config = DatabaseConfig(host="db.example.com", port=5433)
cache_config = CacheConfig(ttl=600)

config = AppConfig(
    name="MyService",
    database=db_config,
    cache=cache_config
)
```

### After Initialization

You can update nested configuration values after initialization:

```python
config = AppConfig()

# Update individual values
config.database.host = "db.example.com"
config.database.port = 5433
config.cache.ttl = 600

# Or replace entire nested configurations
config.database = DatabaseConfig(host="db.example.com", port=5433)
config.cache = {"enabled": True, "ttl": 600}  # Also accepts dictionaries
```

## Multi-level Hierarchy

You can create deeply nested configuration hierarchies by nesting `FieldConf` fields:

```python
# Email configuration
class SmtpConfig(ContainerConf):
    host = FieldString(default="smtp.example.com", help="SMTP server")
    port = FieldInt(default=587, help="SMTP port")
    use_tls = FieldBool(default=True, help="Use TLS")

# Notification configuration with nested email config
class NotificationConfig(ContainerConf):
    enabled = FieldBool(default=True, help="Enable notifications")
    email = FieldConf(SmtpConfig, help="Email configuration")
    sms_provider = FieldString(default="twilio", help="SMS provider")

# Main application config with multiple levels of nesting
class ServiceConfig(ContainerConf):
    name = FieldString(default="MyService", help="Service name")
    database = FieldConf(DatabaseConfig, help="Database configuration")
    notifications = FieldConf(NotificationConfig, help="Notification configuration")
```

You can access multi-level nested configurations using multiple attribute accesses:

```python
config = ServiceConfig()

# Access deeply nested values
print(f"Service name: {config.name}")
print(f"Database host: {config.database.host}")
print(f"SMTP server: {config.notifications.email.host}")
print(f"Use TLS: {config.notifications.email.use_tls}")
```

## Configuration Inheritance

Superconf supports configuration inheritance, allowing you to extend and override configuration classes:

```python
# Base application configuration
class BaseAppConfig(ContainerConf):
    debug = FieldBool(default=False, help="Enable debug mode")
    log_level = FieldString(default="info", help="Logging level")
    database = FieldConf(DatabaseConfig, help="Database configuration")

# Development configuration inherits from base
class DevAppConfig(BaseAppConfig):
    debug = FieldBool(default=True, help="Enable debug mode (overridden)")
    log_level = FieldString(default="debug", help="Logging level (overridden)")
    
    # Override meta attributes
    class Meta:
        extra_fields = True  # Allow extra fields not defined in the class
    
# Production configuration inherits from base
class ProdAppConfig(BaseAppConfig):
    log_level = FieldString(default="warning", help="Logging level (overridden)")
```

When you inherit from a configuration class:
- Fields from the parent class are included in the child class
- Fields defined in the child class override those in the parent
- Meta attributes can be customized in the child class

```python
# Create configuration instances
base_config = BaseAppConfig()
dev_config = DevAppConfig()
prod_config = ProdAppConfig()

print(f"Base debug: {base_config.debug}")          # False
print(f"Dev debug: {dev_config.debug}")            # True
print(f"Prod debug: {prod_config.debug}")          # False (inherited from base)

print(f"Base log level: {base_config.log_level}")  # info
print(f"Dev log level: {dev_config.log_level}")    # debug
print(f"Prod log level: {prod_config.log_level}")  # warning
```

## Meta Configuration

You can customize behavior of configuration classes using the `Meta` inner class:

```python
class CustomConfig(ContainerConf):
    name = FieldString(default="Default", help="Custom name")
    value = FieldInt(default=42, help="Custom value")
    
    class Meta:
        extra_fields = True  # Allow fields not defined in the class
        children_class = LeafInstance  # Custom leaf class for extra fields
```

Common Meta attributes include:
- `extra_fields`: Whether to allow undefined fields (default: False)
- `children_class`: The class to use for child nodes
- `children_classes`: A dictionary mapping field names to specific child classes

## Configuration Merging

You can merge configurations to combine values from multiple sources:

```python
# Base configuration
base_config = AppConfig(
    name="BaseApp",
    database={"host": "base-db", "port": 5432}
)

# Override configuration
override_config = AppConfig(
    debug=True,
    database={"port": 5433, "user": "admin"}
)

# Merge configurations
base_config.merge(override_config)

print(f"Name: {base_config.name}")              # BaseApp (unchanged)
print(f"Debug: {base_config.debug}")            # True (overridden)
print(f"Database host: {base_config.database.host}")  # base-db (unchanged)
print(f"Database port: {base_config.database.port}")  # 5433 (overridden)
print(f"Database user: {base_config.database.user}")  # admin (added)
```

When merging configurations:
- Values from the source configuration override values in the target configuration
- Nested configurations are merged recursively
- New fields from the source are added to the target (if allowed)

## Next Steps

Now that you understand hierarchical configuration in Superconf, you can explore more advanced topics:

- Working with path anchors for file-based configuration
- Loading configuration from files and environment variables
- Creating custom field types with validation
- Using different casts for type conversion 