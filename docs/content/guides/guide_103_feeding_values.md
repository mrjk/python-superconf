# Value feeding



## 2. Loading Nested Configurations

### Using Dictionary Values

```python
config = AppConfig(values={
    'debug': True,
    'database': {
        'host': 'db.example.com',
        'port': 5432,
        'username': 'admin',
        'password': 'secret'
    },
    'redis': {
        'host': 'redis.example.com',
        'port': 6379,
        'db': 1
    }
})

print(config.database.host)     # "db.example.com"
print(config.redis.port)        # 6379
```

### Using Environment Variables

Environment variables for nested configurations follow a hierarchical naming pattern:

```bash
# Database configuration
export APP_DATABASE_HOST="db.example.com"
export APP_DATABASE_PORT="5432"
export APP_DATABASE_USERNAME="admin"
export APP_DATABASE_PASSWORD="secret"

# Redis configuration
export APP_REDIS_HOST="redis.example.com"
export APP_REDIS_PORT="6379"
export APP_REDIS_DB="1"

# Main configuration
export APP_DEBUG="true"
```
