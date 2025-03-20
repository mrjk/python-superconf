# How to Use Configuration Inheritance

<div align="center">
  <p><em>Learn how to create reusable configuration hierarchies in Superconf</em></p>
</div>

<p align="right">
  <a href="../README.md">📚 Main</a> |
  <a href="README.md">⚡ How-To Guides</a> |
  <a href="03_custom_field_types.md">⏮️ Previous: Custom Field Types</a>
</p>

---

This guide demonstrates how to use inheritance in Superconf to create reusable, extensible configuration classes.

## Basic Configuration Inheritance

Inheritance allows you to define a base configuration class and extend it with more specific ones:

```python
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

# Base configuration class
class BaseConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    log_level = FieldString(default="info")
    timeout = FieldInt(default=30)

# Development environment configuration
class DevConfig(BaseConfig):
    debug = FieldBool(default=True)  # Override default
    log_level = FieldString(default="debug")  # Override default
    hot_reload = FieldBool(default=True)  # Add new field

# Production environment configuration
class ProdConfig(BaseConfig):
    log_level = FieldString(default="warning")  # Override default
    timeout = FieldInt(default=60)  # Override default
    worker_count = FieldInt(default=4)  # Add new field

# Create instances
base = BaseConfig()
dev = DevConfig()
prod = ProdConfig()

print(f"Base config: debug={base.debug}, log_level={base.log_level}")
print(f"Dev config: debug={dev.debug}, log_level={dev.log_level}, hot_reload={dev.hot_reload}")
print(f"Prod config: debug={prod.debug}, log_level={prod.log_level}, worker_count={prod.worker_count}")
```

Output:
```
Base config: debug=False, log_level=info
Dev config: debug=True, log_level=debug, hot_reload=True
Prod config: debug=False, log_level=warning, worker_count=4
```

## Multi-level Inheritance

You can create deeper inheritance hierarchies:

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList
from superconf.configuration import ContainerConf

# Base configuration
class BaseConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    log_level = FieldString(default="info")

# Environment-specific base configurations
class DevBaseConfig(BaseConfig):
    debug = FieldBool(default=True)
    log_level = FieldString(default="debug")
    allowed_hosts = FieldList(default=["localhost", "127.0.0.1"])

class ProdBaseConfig(BaseConfig):
    log_level = FieldString(default="warning")
    allowed_hosts = FieldList(default=["myapp.com", "api.myapp.com"])

# Application-specific configurations
class WebAppDevConfig(DevBaseConfig):
    port = FieldInt(default=3000)
    hot_reload = FieldBool(default=True)

class ApiDevConfig(DevBaseConfig):
    port = FieldInt(default=8000)
    auth_required = FieldBool(default=False)

class WebAppProdConfig(ProdBaseConfig):
    port = FieldInt(default=80)
    worker_count = FieldInt(default=4)

class ApiProdConfig(ProdBaseConfig):
    port = FieldInt(default=443)
    auth_required = FieldBool(default=True)
    rate_limit = FieldInt(default=100)

# Create instances
web_dev = WebAppDevConfig()
api_dev = ApiDevConfig()
web_prod = WebAppProdConfig()
api_prod = ApiProdConfig()

print(f"Web Dev: debug={web_dev.debug}, port={web_dev.port}, hot_reload={web_dev.hot_reload}")
print(f"API Dev: debug={api_dev.debug}, port={api_dev.port}, auth={api_dev.auth_required}")
print(f"Web Prod: debug={web_prod.debug}, port={web_prod.port}, workers={web_prod.worker_count}")
print(f"API Prod: debug={api_prod.debug}, port={api_prod.port}, auth={api_prod.auth_required}, rate_limit={api_prod.rate_limit}")
```

## Inheriting with Nested Configurations

You can use inheritance with nested configurations:

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf
from superconf.configuration import ContainerConf

# Nested configurations
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString(default="myapp")
    user = FieldString(default="dbuser")
    password = FieldString()  # Required

class DevDatabaseConfig(DatabaseConfig):
    password = FieldString(default="devpassword")  # Override to provide a default

class ProdDatabaseConfig(DatabaseConfig):
    host = FieldString(default="db.example.com")
    connection_pool = FieldInt(default=10)

# Base configuration
class BaseConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)

# Environment-specific configurations
class DevConfig(BaseConfig):
    debug = FieldBool(default=True)
    database = FieldConf(DevDatabaseConfig)  # Use the Dev-specific database config

class ProdConfig(BaseConfig):
    app_name = FieldString(default="MyApp-Production")
    database = FieldConf(ProdDatabaseConfig)  # Use the Prod-specific database config

# Create instances
dev = DevConfig()
prod = ProdConfig()

print(f"Dev DB: {dev.database.host}:{dev.database.port}, pass={dev.database.password}")
print(f"Prod DB: {prod.database.host}:{prod.database.port}, pool={prod.database.connection_pool}")
```

Output:
```
Dev DB: localhost:5432, pass=devpassword
Prod DB: db.example.com:5432, pool=10
```

## Meta Configuration Inheritance

You can also inherit and override Meta configurations:

```python
from superconf.fields import FieldString, FieldInt, FieldDict
from superconf.configuration import ContainerConf

# Base configuration with Meta settings
class BaseConfig(ContainerConf):
    name = FieldString(default="Base")
    version = FieldString(default="1.0.0")
    
    class Meta:
        extra_fields = False  # Don't allow extra fields
        children_class = None  # Default leaf class

# Derived configuration with overridden Meta
class FlexibleConfig(BaseConfig):
    options = FieldDict(default={})
    
    class Meta:
        extra_fields = True  # Allow extra fields
        # children_class is inherited

# Create instances
base = BaseConfig()
flexible = FlexibleConfig()

# This will raise an error (extra_fields=False)
try:
    base.unknown_field = "value"
    print("Should not reach here")
except Exception as e:
    print(f"Base error: {e}")

# This will work (extra_fields=True)
try:
    flexible.unknown_field = "value"
    print(f"Flexible extra field: {flexible.unknown_field}")
except Exception as e:
    print(f"Flexible error: {e}")
```

## Mixin-Style Configuration

You can create configuration mixins for common settings:

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldList
from superconf.configuration import ContainerConf

# Configuration mixins for common settings
class LoggingConfigMixin(ContainerConf):
    log_level = FieldString(default="info")
    log_file = FieldString(default="app.log")
    log_format = FieldString(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

class SecurityConfigMixin(ContainerConf):
    ssl_enabled = FieldBool(default=False)
    ssl_cert = FieldString(default="cert.pem")
    ssl_key = FieldString(default="key.pem")

class PerformanceConfigMixin(ContainerConf):
    worker_count = FieldInt(default=1)
    connection_timeout = FieldInt(default=30)
    max_requests = FieldInt(default=1000)

# Application-specific configurations using mixins
class WebAppConfig(LoggingConfigMixin, SecurityConfigMixin):
    app_name = FieldString(default="WebApp")
    port = FieldInt(default=8000)
    debug = FieldBool(default=False)

class ApiConfig(LoggingConfigMixin, SecurityConfigMixin, PerformanceConfigMixin):
    app_name = FieldString(default="API")
    port = FieldInt(default=9000)
    allowed_origins = FieldList(default=["*"])

# Create instances
web = WebAppConfig()
api = ApiConfig()

print(f"Web: log_level={web.log_level}, ssl_enabled={web.ssl_enabled}")
print(f"API: log_level={api.log_level}, worker_count={api.worker_count}, ssl_enabled={api.ssl_enabled}")
```

## Dynamic Configuration Selection

You can select configurations dynamically:

```python
import os
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

# Base configuration
class BaseConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    log_level = FieldString(default="info")

# Environment-specific configurations
class DevConfig(BaseConfig):
    debug = FieldBool(default=True)
    log_level = FieldString(default="debug")

class TestConfig(BaseConfig):
    debug = FieldBool(default=True)
    log_level = FieldString(default="info")

class StagingConfig(BaseConfig):
    log_level = FieldString(default="info")

class ProdConfig(BaseConfig):
    log_level = FieldString(default="warning")

# Configuration factory
def get_config():
    """Return the appropriate configuration class based on environment"""
    env = os.environ.get("APP_ENV", "dev").lower()
    
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "staging": StagingConfig,
        "prod": ProdConfig
    }
    
    config_class = configs.get(env, DevConfig)
    return config_class()

# Usage
os.environ["APP_ENV"] = "dev"
config = get_config()
print(f"Dev: debug={config.debug}, log_level={config.log_level}")

os.environ["APP_ENV"] = "prod"
config = get_config()
print(f"Prod: debug={config.debug}, log_level={config.log_level}")
```

## Configuration Registration Pattern

You can create a registration pattern for configurations:

```python
from superconf.fields import FieldString, FieldInt, FieldBool
from superconf.configuration import ContainerConf

# Configuration registry
class ConfigRegistry:
    _configs = {}
    
    @classmethod
    def register(cls, name, config_class):
        """Register a configuration class"""
        cls._configs[name] = config_class
    
    @classmethod
    def get(cls, name, **kwargs):
        """Get a configuration instance by name"""
        if name not in cls._configs:
            raise ValueError(f"Unknown configuration: {name}")
        return cls._configs[name](**kwargs)
    
    @classmethod
    def list_configs(cls):
        """List available configurations"""
        return list(cls._configs.keys())

# Base configuration
class BaseConfig(ContainerConf):
    app_name = FieldString(default="MyApp")
    debug = FieldBool(default=False)

# Register configurations
ConfigRegistry.register("base", BaseConfig)

# Development configuration
class DevConfig(BaseConfig):
    debug = FieldBool(default=True)
    port = FieldInt(default=3000)

# Register more configurations
ConfigRegistry.register("dev", DevConfig)

# Production configuration
class ProdConfig(BaseConfig):
    port = FieldInt(default=80)
    worker_count = FieldInt(default=4)

# Register more configurations
ConfigRegistry.register("prod", ProdConfig)

# Usage
print(f"Available configs: {ConfigRegistry.list_configs()}")

base = ConfigRegistry.get("base")
dev = ConfigRegistry.get("dev")
prod = ConfigRegistry.get("prod")

print(f"Base: app_name={base.app_name}, debug={base.debug}")
print(f"Dev: app_name={dev.app_name}, debug={dev.debug}, port={dev.port}")
print(f"Prod: app_name={prod.app_name}, debug={prod.debug}, port={prod.port}, workers={prod.worker_count}")

# Create custom instance with overrides
custom = ConfigRegistry.get("dev", app_name="CustomApp", port=5000)
print(f"Custom: app_name={custom.app_name}, debug={custom.debug}, port={custom.port}")
```

## Advanced: Configuration Factories

You can create factory functions for complex configurations:

```python
from superconf.fields import FieldString, FieldInt, FieldBool, FieldConf, FieldList
from superconf.configuration import ContainerConf

# Base configurations
class DatabaseConfig(ContainerConf):
    host = FieldString(default="localhost")
    port = FieldInt(default=5432)
    name = FieldString()
    user = FieldString()
    password = FieldString()

class CacheConfig(ContainerConf):
    enabled = FieldBool(default=True)
    host = FieldString(default="localhost")
    port = FieldInt(default=6379)

class BaseAppConfig(ContainerConf):
    name = FieldString(default="MyApp")
    debug = FieldBool(default=False)
    database = FieldConf(DatabaseConfig)
    cache = FieldConf(CacheConfig)

# Configuration factory function
def create_app_config(env="dev", name=None, **overrides):
    """Create a configuration tailored for the specified environment"""
    
    # Start with the base configuration
    config_class = type(f"{env.capitalize()}AppConfig", (BaseAppConfig,), {})
    
    # Apply environment-specific defaults
    if env == "dev":
        # Development environment
        config_class.debug = FieldBool(default=True)
        config_class.allowed_hosts = FieldList(default=["localhost", "127.0.0.1"])
        
        # Override database defaults for dev
        dev_db = type("DevDatabaseConfig", (DatabaseConfig,), {
            "name": FieldString(default="myapp_dev"),
            "user": FieldString(default="dev_user"),
            "password": FieldString(default="dev_password")
        })
        config_class.database = FieldConf(dev_db)
        
    elif env == "test":
        # Test environment
        config_class.debug = FieldBool(default=True)
        config_class.testing = FieldBool(default=True)
        
        # Override database defaults for test
        test_db = type("TestDatabaseConfig", (DatabaseConfig,), {
            "name": FieldString(default="myapp_test"),
            "user": FieldString(default="test_user"),
            "password": FieldString(default="test_password")
        })
        config_class.database = FieldConf(test_db)
        
    elif env == "prod":
        # Production environment
        config_class.worker_count = FieldInt(default=4)
        config_class.allowed_hosts = FieldList(default=["myapp.com", "www.myapp.com"])
        
        # Override database defaults for prod
        prod_db = type("ProdDatabaseConfig", (DatabaseConfig,), {
            "host": FieldString(default="db.myapp.com"),
            "name": FieldString(default="myapp_prod"),
            "connection_pool": FieldInt(default=10)
        })
        config_class.database = FieldConf(prod_db)
        
        # Override cache defaults for prod
        prod_cache = type("ProdCacheConfig", (CacheConfig,), {
            "host": FieldString(default="cache.myapp.com"),
        })
        config_class.cache = FieldConf(prod_cache)
    
    # Create an instance with the provided overrides
    config_kwargs = {}
    if name:
        config_kwargs["name"] = name
    config_kwargs.update(overrides)
    
    return config_class(**config_kwargs)

# Usage
dev_config = create_app_config(env="dev")
test_config = create_app_config(env="test", name="TestApp")
prod_config = create_app_config(
    env="prod", 
    database={"host": "custom-db.example.com"}
)

print(f"Dev: debug={dev_config.debug}, db={dev_config.database.name}")
print(f"Test: name={test_config.name}, testing={test_config.testing}, db={test_config.database.name}")
print(f"Prod: workers={prod_config.worker_count}, db_host={prod_config.database.host}")
```

## Best Practices

When using configuration inheritance in Superconf:

1. **Create a clear hierarchy**: Design your configuration inheritance to match your application's structure.

2. **Start with a well-designed base class**: Include common fields that will be used across all configurations.

3. **Use composition for complex configurations**: Use nested configurations for logical grouping of related settings.

4. **Override field defaults, not field types**: Maintain consistent field types across inherited configurations.

5. **Create configuration mixins**: Use mixins for reusable groups of related settings.

6. **Consider factory functions**: For complex configuration logic, use factory functions instead of direct inheritance.

7. **Document your configuration classes**: Clearly document the purpose and usage of each configuration class.

8. **Use Meta configurations intentionally**: Be explicit about Meta attributes in derived classes.

9. **Test your configurations**: Verify that inheritance works as expected with unit tests.

10. **Don't over-inherit**: Keep your inheritance hierarchy shallow to maintain readability.

## Summary

Configuration inheritance in Superconf allows you to:
- Share common settings across multiple configurations
- Override defaults for specific environments or use cases
- Compose configurations from reusable components
- Create factory functions for complex configuration logic

By using inheritance effectively, you can keep your configuration code DRY (Don't Repeat Yourself) while maintaining flexibility for different environments and use cases. 