"XDG Support"

# pylint: disable=too-few-public-methods, too-many-nested-blocks, too-many-branches

import logging
import os
from pathlib import Path

# pylint: disable=unused-import
from pprint import pprint

from superconf.casts import AsBest, AsList, AsString
from superconf.common import (
    from_json,
    from_yaml,
    read_file,
    to_json,
    to_yaml,
    write_file,
)
from superconf.configuration import ConfigurationDict
from superconf.fields import Field

logger = logging.getLogger(__name__)


# ====================================
# Exceptions and casts
# ====================================


class XDGException(Exception):
    "XDG error"


class CastEnvColonValues(AsList):
    "Cast env value as list with colon seprated values"

    def __init__(self, **kwargs):

        self.as_best = AsBest()
        super().__init__(**kwargs)

    def __call__(self, value):
        # print ("CALL CastEnvColonValues", self, value )
        # out = traceback.print_stack()
        # print ("EXECUTED", out)

        out = super().__call__(value)
        ret = []
        for x in out:
            x = os.path.expandvars(x)
            x = self.as_best(x)
            ret.append(x)

        return ret


# ====================================
# XDG Configuration
# ====================================

# Create cast instances
cast_env = AsBest()  # Try fetch best type
cast_env_colon = AsList(delimiter=":")  # We force lists with delimiter


class UserConfig(ConfigurationDict):
    "User var support"

    meta__env_parents = False  # Not parent keys
    meta__env_name = ""  # No prefix for environment vars

    HOME = Field(default="/home/user", cast=cast_env)
    USER = Field(default="user", cast=cast_env)
    UID = Field(default="1000", cast=cast_env)
    LANG = Field(default="en_US.utf8", cast=cast_env)

    SHELL = Field(default="/bin/bash", cast=cast_env)
    SHLVL = Field(default="/bin/bash", cast=cast_env)
    PWD = Field(default="/", cast=cast_env)
    OLDPWD = Field(default="/", cast=cast_env)
    PATH = Field(default="/", cast=cast_env_colon)
    DISPLAY = Field(default="", cast=cast_env)

    WEIRD = Field(cast=cast_env)


class XDGConfig(UserConfig):
    "Base class with XDG var support"

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

    # Legacy commands
    def get_config_file(self, name=None):
        """Get config file path."""
        return self.get_file("XDG_CONFIG_HOME", name)

    def get_config_dir(self, name=None):
        """Get config directory path."""
        return self.get_dir("XDG_CONFIG_HOME", name)

    # Internal API
    def _parse_path(self, values, name=None, prefix=None, extensions=None):
        """Parse and expand path."""

        found = False
        extensions = extensions or []
        ret = []
        for path in values:

            path = os.path.expandvars(path)
            if isinstance(prefix, str):
                path = os.path.join(path, prefix)
            path = path.rstrip("/")

            if extensions:
                # File lookup only

                if name:

                    # Validate name doesn't already end with any extension
                    name, file_extension = os.path.splitext(name)
                    if file_extension:
                        file_extension = file_extension.lstrip(".")
                        if file_extension not in extensions:
                            name = f"{name}.{file_extension}"
                        else:
                            extensions = [file_extension]

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

    def read_file(self, item, name=None, missing_ok=True):
        "Read a file content"

        # Fetch best file
        files = self.get_file(item, name=name)
        if not isinstance(files, list):
            files = [files]

        # Return error if no files
        if not files:
            if name:
                raise XDGException(f"Could not find any file in {item} called {name}")
            raise XDGException(f"Could not find any file in {item}")

        # Return first file
        out = None
        found = False
        for file in files:
            file = str(file)

            if not os.path.isfile(file):
                continue

            found = True
            logger.info("Read file %s", file)

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

        if not found:
            if not missing_ok:
                raise XDGException(f"Could not find any file in {str(files[0])}")

        return out

    def write_file(self, item, data, name=None):
        "Write content to file"

        # Fetch best file
        files = self.get_file(item, name=name)
        if not isinstance(files, list):
            files = [files]

        # Return error if no files
        if not files:
            if name:
                raise XDGException(f"Could not find any file in {item} called {name}")
            raise XDGException(f"Could not find any file in {item}")

        # Write only on the first file
        files = [files[0]]
        for file in files:
            file = str(file)

            # fcontent = read_file(file)
            if file.endswith("yaml") or file.endswith("yml"):
                out = to_yaml(data)
            elif file.endswith("json"):
                out = to_json(data)
            elif file.endswith("toml"):
                raise NotImplementedError("Toml support not implemented yet")
            elif file.endswith("ini"):
                raise NotImplementedError("Ini support is not implemented yet")
            else:
                raise NotImplementedError(f"Format not supported: {file}")

            logger.info("Write data in file %s", file)
            write_file(file, out)
            break

    def get_file(self, item, name=None):
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
        if extensions:  # Only append first extension if list is not empty
            extensions.append(extensions[0])

        # Parse paths
        app_name = self.query_cfg("app_name", default=None)
        if not isinstance(app_name, str):
            root = self.get_hierarchy()[-1]
            app_name = root.__class__.__name__
        assert app_name

        # print ("=== PARSE PATH", values, name, app_name, extensions)
        ret = self._parse_path(
            values, name=name, prefix=app_name, extensions=extensions
        )

        if return_one is True:
            return ret[0] if len(ret) > 0 else None

        return ret

    def get_dir(self, item, name=None):
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
        app_name = self.query_cfg("app_name", default=None)
        if not app_name or not isinstance(app_name, str):
            root = self.get_hierarchy()[-1]
            app_name = root.__class__.__name__

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


class ExtraConfig(XDGConfig):
    "Extra var support"

    GIT_AUTHOR_EMAIL = Field()
    GIT_AUTHOR_NAME = Field()
    GIT_COMMITTER_EMAIL = Field()
    GIT_COMMITTER_NAME = Field()

    TERM = Field()
    SSH_AGENT_PID = Field()
    SSH_AUTH_SOCK = Field()
    XDG_SEAT = Field()
    XDG_SEAT_PATH = Field()
    XDG_SESSION_CLASS = Field()
    XDG_SESSION_DESKTOP = Field()
    XDG_SESSION_ID = Field()
    XDG_SESSION_PATH = Field()
    XDG_SESSION_TYPE = Field()
    VIRTUAL_ENV = Field()
    LOGNAME = Field()
    GNUPGHOME = Field()
    # GITEA_LOGIN = Field()
    # GITEA_SERVER_URL = Field()
    # GH_REPO = Field()
    # GH_TOKEN = Field()
    # DIRENV_DIR = Field()
    # DIRENV_FILE = Field()
    DESKTOP_SESSION = Field()
    DBUS_SESSION_BUS_ADDRESS = Field()
