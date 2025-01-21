"XDG Support"

# pylint: disable=too-few-public-methods, too-many-nested-blocks, too-many-branches

import os
from pathlib import Path

from superconf.common import from_json, from_yaml, read_file
from superconf.configuration import ConfigurationDict
from superconf.fields import Field

# ====================================
# Exceptions and casts
# ====================================


class XDGException(Exception):
    "XDG error"


class AsSplitString:
    """
    Split string to list
    """

    def __init__(self, sep=" "):
        self.sep = sep

    def __call__(self, value):
        # print ("CALL AsSplitString", self, value)

        # print (f"\n\n === PRINT CASTLIST {value}===  \n", self)
        # assert isinstance(value, str), f"Got: {type(value)}: {value}"

        if isinstance(value, str):
            return value.split(self.sep)

        assert isinstance(value, list), f"Got: {type(value)}: {value}"

        return value


class CastEnvValue:
    "Cast simple environment var, as string"

    def __call__(self, value):
        # print ("CALL CastEnvValue", self, value)
        out = os.path.expandvars(value)
        return out


class CastEnvColonValues(AsSplitString, CastEnvValue):
    "Cast env value as list with colon seprated values"

    def __call__(self, value):
        # print ("CALL CastEnvColonValues", self, value )
        # out = traceback.print_stack()
        # print ("EXECUTED", out)

        out = super().__call__(value)
        out = [os.path.expandvars(x) for x in out]

        # out = super(AsSplitString, self).__call__(out)

        return out


# ====================================
# XDG Configuration
# ====================================

# Create cast instances
cast_env = CastEnvValue()
cast_env_colon = CastEnvColonValues(sep=":")


class UserConfig(ConfigurationDict):
    "User var support"

    meta__env_parents = False
    meta__env_name = ""

    HOME = Field(default="/home/user", cast=cast_env)

    USER = Field(default="user", cast=cast_env)

    UID = Field(default="1000", cast=cast_env)

    SHELL = Field(default="/bin/bash", cast=cast_env)

    SHLVL = Field(default="/bin/bash", cast=cast_env)

    PWD = Field(default="/", cast=cast_env)
    OLDPWD = Field(default="/", cast=cast_env)

    PATH = Field(default="/", cast=cast_env_colon)

    LANG = Field(default="en_US.utf8", cast=cast_env)

    DISPLAY = Field(default="", cast=cast_env)


class ExtraConfig(ConfigurationDict):
    "Extra var support"

    meta__env_parents = False
    meta__env_name = ""

    GIT_AUTHOR_EMAIL = Field(default="user@email.tld", cast=cast_env)
    GIT_AUTHOR_NAME = Field(default="user", cast=cast_env)

    # TERM
    # SSH_AGENT_PID, SSH_AUTH_SOCK
    # XDG_SEAT
    # XDG_SEAT_PATH
    # XDG_SESSION_CLASS
    # XDG_SESSION_DESKTOP
    # XDG_SESSION_ID
    # XDG_SESSION_PATH
    # XDG_SESSION_TYPE
    # VIRTUAL_ENV
    # LOGNAME
    # GNUPGHOME
    # GIT_COMMITTER_EMAIL
    # GIT_COMMITTER_NAME
    # GITEA_LOGIN
    # GITEA_SERVER_URL
    # GH_REPO
    # GH_TOKEN
    # DIRENV_DIR
    # DIRENV_FILE
    # DESKTOP_SESSION
    # DBUS_SESSION_BUS_ADDRESS


class XDGConfig(ConfigurationDict):
    "Base class with XDG var support"

    meta__env_parents = False
    meta__env_name = ""
    meta__xdg_file_fmt = [
        "yml",
        "yaml",
        "json",
        "toml",
        # "ini",
    ]

    XDG_CONFIG_HOME = Field(default="$HOME/.config", cast=cast_env)  # Like: /etc
    XDG_DATA_HOME = Field(
        default="$HOME/.local/share", cast=cast_env
    )  # Like: /usr/share
    XDG_CACHE_HOME = Field(default="$HOME/.cache", cast=cast_env)  # Like: /var/cache
    XDG_STATE_HOME = Field(
        default="$HOME/.local/state", cast=cast_env
    )  # Like: /var/lib

    XDG_RUNTIME_DIR = Field(
        default="/run/user/$UID", cast=cast_env
    )  # Like: /run/user/$UID for pam_systemd

    XDG_CONFIG_DIRS = Field(default="/etc/xdg", cast=cast_env_colon)
    XDG_DATA_DIRS = Field(default="/usr/local/share:/usr/share", cast=cast_env_colon)

    def get_config_file(self, name=None):
        """Get config file path."""
        return self._get_file("XDG_CONFIG_HOME", name)

    def get_config_dir(self, name=None):
        """Get config directory path."""
        return self._get_dir("XDG_CONFIG_HOME", name)

    # def get_data_file(self, name=None):
    #     """Get data file path."""
    #     return self._get_file('XDG_DATA_HOME', name)

    # def get_cache_file(self, name=None):
    #     """Get cache file path."""
    #     return self._get_file('XDG_CACHE_HOME', name)

    # def get_state_file(self, name=None):
    #     """Get state file path."""
    #     return self._get_file('XDG_STATE_HOME', name)

    # def get_runtime_file(self, name=None):
    #     """Get runtime file path."""
    #     return self._get_file('XDG_RUNTIME_DIR', name)

    # def get_data_dir(self, name=None):
    #     """Get data directory path."""
    #     return self._get_dir('XDG_DATA_HOME', name)

    # def get_cache_dir(self, name=None):
    #     """Get cache directory path."""
    #     return self._get_dir('XDG_CACHE_HOME', name)

    # def get_state_dir(self, name=None):
    #     """Get state directory path."""
    #     return self._get_dir('XDG_STATE_HOME', name)

    # def get_runtime_dir(self, name=None):
    #     """Get runtime directory path."""
    #     return self._get_dir('XDG_RUNTIME_DIR', name)

    def _parse_path(self, values, name=None, prefix=None, extensions=None):
        """Parse and expand path."""

        found = False
        extensions = extensions or []
        ret = []
        for path in values:

            path = os.path.expandvars(path)
            if isinstance(prefix, str):
                path = os.path.join(path, prefix)

            if extensions:
                # File lookup only

                if name:

                    # Validate name doesn't already end with any extension
                    for ext in extensions:
                        if name.endswith(f".{ext}"):
                            name = name[: -len(ext) - 1]  # Remove the extension

                    default_path = os.path.join(path, f"{name}.{extensions[0]}")
                    found = False
                    for ext in extensions:
                        if found is False:
                            fname = f"{name}.{ext}"
                            fpath = os.path.join(path, fname)
                            if os.path.isfile(fpath):
                                path = fpath
                                found = True
                else:

                    default_path = f"{path}.{extensions[0]}"
                    found = False
                    for ext in extensions:
                        if found is False:
                            fpath = f"{path}.{ext}"
                            if os.path.isfile(fpath):
                                path = fpath
                                found = True

                path = path if found else default_path
            else:
                # Only for directory lookup
                if name:
                    path = os.path.join(path, f"{name}")

                else:
                    path = f"{path}"

            path = Path(path)
            ret.append(path)

        # print ("MATCHED", found, ret)
        return ret

    def read_file(self, item, name=None):
        "Read a file content"

        # Fetch best file
        files = self._get_file(item, name=name)
        if not isinstance(files, list):
            files = [files]

        # Return error if no files
        if not files:
            if name:
                raise XDGException(f"Could not find any file in {item} called {name}")
            raise XDGException(f"Could not find any file in {item}")

        # Return first file
        out = None
        for file in files:
            file = str(file)

            if not os.path.isfile(file):
                continue

            fcontent = read_file(file)
            if file.endswith("yaml") or file.endswith("yml"):
                out = from_yaml(fcontent)
            elif file.endswith("json"):
                out = from_json(fcontent)
            elif file.endswith("toml"):
                raise NotImplementedError("Toml support not implemented yet")
            elif file.endswith("ini"):
                raise NotImplementedError("Ini support is not implemented yet")
            else:
                raise NotImplementedError(f"Format not supported: {file}")

            break

        return out

    def _get_file(self, item, name=None):
        """Get file path for given XDG item."""

        # Fetch current value
        if not hasattr(self, item.upper()):
            choices = list(self.get_values().keys())
            raise XDGException(f"Unknown item: {item}, choose one of: {choices}")
        values = self[item]

        # Convert to list
        return_one = True
        if isinstance(values, list):
            return_one = False
        else:
            values = [values]
        assert isinstance(values, list), f"Got: {values}"

        # Prepare extensions
        extensions = list(self.meta__xdg_file_fmt)
        extensions.append(extensions[0])

        # Parse paths
        # print ("YOOOOOOOOOOOOOIII1")
        app_name = self.query_cfg("app_name", default=None)
        # print ("YOOOOOOOOOOOOOIII2")
        if not isinstance(app_name, str):
            root = self.get_hierarchy()[-1]
            app_name = root.__class__.__name__

        # print ("=== PARSE PATH", values, name, app_name, extensions)
        ret = self._parse_path(
            values, name=name, prefix=app_name, extensions=extensions
        )

        if return_one is True:
            return ret[0] if len(ret) > 0 else None

        return ret

    def _get_dir(self, item, name=None):
        """Get directory path for given XDG item."""

        # Fetch current value
        if not hasattr(self, item.upper()):
            choices = list(self.get_values().keys())
            raise XDGException(f"Unknown item: {item}, choose one of: {choices}")
        values = self[item]

        # Convert to list
        return_one = True
        if isinstance(values, list):
            return_one = False
        else:
            values = [values]
        assert isinstance(values, list), f"Got: {values}"

        # Prepare extensions
        extensions = []

        # Parse paths
        app_name = self.query_cfg("app_name")
        ret = self._parse_path(
            values, name=name, prefix=app_name, extensions=extensions
        )

        if return_one is True:
            return ret[0] if len(ret) > 0 else None

        return ret

    # def _process_vars(self, item, name=None):
    #     """Process XDG variables into paths."""
    #     paths = self._resolve_var(item)
    #     out = []
    #     for path in paths:
    #         parsed = self._parse_path(path)
    #         if name:
    #             parsed = parsed / name
    #         out.append(parsed)
    #     return out

    # def _resolve_var(self, item):
    #     """Resolve XDG variable to list of paths."""
    #     if not hasattr(self, item):
    #         choices = list(self.get_values().keys())
    #         raise XDGException(f"Unknown item: {item}, choose one of: {choices}")

    #     value = self[item]
    #     if isinstance(value, str):
    #         value = [value]
    #     assert isinstance(value, list), f"Got: {value}"
    #     return value

    # def _parse_path(self, path):
    #     """Parse and expand path."""
    #     app_name = self.query_cfg("app_name")
    #     out = os.path.join(path, app_name)
    #     out = os.path.expandvars(out)
    #     return Path(out)

    # def find_first_file(self, pdirs):
    #     "Return configuration first existing configfile"

    #     extensions = self.query_cfg("xdg_file_fmt")
    #     extensions.append(extensions[0])

    #     # Try each file
    #     fname = None
    #     for pdir in pdirs:
    #         pdir = pdir.absolute()
    #         for ext in extensions:
    #             fname = f"{pdir}.{ext}"
    #             if os.path.isfile(fname):
    #                 break

    #     return Path(fname)
