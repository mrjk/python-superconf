"""Dynamic list of children via ConfigurationList + children_class."""

from pprint import pprint

from superconf import (
    ConfigurationList,
    ConfigurationObj,
    FieldConf,
    FieldInt,
    FieldString,
)


class ServerConfig(ConfigurationObj):
    """One server entry."""

    host = FieldString(default="localhost", help="Server hostname")
    port = FieldInt(default=8080, help="Server port")
    role = FieldString(default="worker", help="Server role")


class ServerList(ConfigurationList):
    """List of servers."""

    class Meta:
        children_class = ServerConfig
        default = [
            {"host": "primary.example.com", "role": "primary"},
            {"host": "secondary.example.com", "role": "backup"},
        ]


class AppConfig(ConfigurationObj):
    """App holding a dynamic server list."""

    app_name = FieldString(default="ClusterManager")
    servers = FieldConf(ServerList, help="Cluster servers")


app = AppConfig()

print(f"app_name={app.app_name!r}")
print(f"server count={len(app.servers)}")
pprint(app.servers.get_value())

assert len(app.servers) == 2
assert app.servers(0).host == "primary.example.com"
assert app.servers(0).port == 8080  # default filled in
assert app.servers[1]["role"] == "backup"

print("\nPer-server access:")
for index, server in enumerate(app.servers):
    print(f"  [{index}] host={server.host!r} port={server.port} role={server.role!r}")

# Replace list contents
app.servers.set_value(
    [
        {"host": "new.example.com", "port": 9000, "role": "primary"},
    ]
)
assert len(app.servers) == 1
assert app.servers(0).port == 9000

print("\nAfter set_value:")
pprint(app.servers.get_value())

print("\nOK")
