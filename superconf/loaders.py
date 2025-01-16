"Loaders library"

# pylint: disable=unnecessary-dunder-call, unused-argument


import os
from configparser import ConfigParser, MissingSectionHeaderError, NoOptionError
from glob import glob

from classyconf.parsers import EnvFileParser

from .common import NOT_SET
from .exceptions import InvalidConfigurationFile, InvalidPath, MissingSettingsSection


class EnvPrefix:
    """
    A utility class for namespacing environment variables with a prefix.

    Since the environment is a global dictionary, it is a good practice to
    namespace your settings by using a unique prefix like ``MY_APP_``.

    Args:
        prefix (str): The prefix to prepend to environment variable names. Defaults to "".

    Example:
        >>> prefix = EnvPrefix("MYAPP_")
        >>> prefix("database_url")
        'MYAPP_DATABASE_URL'
    """

    def __init__(self, prefix=""):
        self.prefix = prefix

    def __call__(self, value):
        """
        Transform a configuration key into an environment variable name.

        Args:
            value (str): The configuration key to transform.

        Returns:
            str: The environment variable name with the prefix applied and converted to uppercase.
        """
        value = str(value)
        return f"{self.prefix}{value.upper()}"

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.prefix}")'


def _get_args(parser):
    """
    Convert arguments extracted from an ArgumentParser to a dictionary.

    Args:
        parser (argparse.ArgumentParser): An ArgumentParser instance.

    Returns:
        dict: Dictionary containing the parsed CLI arguments, excluding those with NOT_SET values.
    """
    args = vars(parser.parse_args()).items()
    return {key: val for key, val in args if not isinstance(val, type(NOT_SET))}


class AbstractConfigurationLoader:
    """
    Abstract base class for configuration loaders.

    This class defines the interface that all configuration loaders must implement.
    Configuration loaders are responsible for loading configuration values from
    different sources (files, environment, etc.).
    """

    def __repr__(self):
        raise NotImplementedError()  # pragma: no cover

    def __contains__(self, item):
        """Check if a configuration key exists in this loader."""
        raise NotImplementedError()  # pragma: no cover

    def __getitem__(self, item):
        """Retrieve a configuration value by key."""
        raise NotImplementedError()  # pragma: no cover

    def check(self):
        """
        Verify if the configuration source is valid and accessible.

        Returns:
            bool: True if the configuration source is valid, False otherwise.
        """
        return True

    def reset(self):
        """Reset the loader's internal state."""

    # pylint: disable=unused-argument
    def contains(self, config, item):
        """
        Check if a configuration key exists in this loader.

        Args:
            config: The configuration object.
            item (str): The configuration key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return self.__contains__(item)
        # raise NotImplementedError()  # pragma: no cover

    def getitem(self, config, item):
        """
        Retrieve a configuration value by key.

        Args:
            config: The configuration object.
            item (str): The configuration key to retrieve.

        Returns:
            The configuration value for the given key.

        Raises:
            KeyError: If the key doesn't exist.
        """
        return self.__getitem__(item)
        # raise NotImplementedError()  # pragma: no cover


class CommandLine(AbstractConfigurationLoader):
    """
    Configuration loader that extracts settings from command line arguments.

    This loader uses an argparse.ArgumentParser to extract configuration values
    from command line arguments.

    Args:
        parser (argparse.ArgumentParser): The parser instance to extract variables from.
        get_args (callable): Optional function to extract args from the parser.
                           Defaults to the get_args function.
    """

    # noinspection PyShadowingNames
    def __init__(self, parser, get_args=_get_args):
        """
        :param parser: An `argparse` parser instance to extract variables from.
        :param function get_args: A function to extract args from the parser.
        :type parser: argparse.ArgumentParser
        """
        self.parser = parser
        self.configs = get_args(self.parser)

    def __repr__(self):
        return f"{self.__class__.__name__}(parser={self.parser})"

    def __contains__(self, item):
        """Check if a configuration key exists in the parsed arguments."""
        return item in self.configs

    def __getitem__(self, item):
        """Retrieve a configuration value from the parsed arguments."""
        return self.configs[item]


class IniFile(AbstractConfigurationLoader):
    """
    Configuration loader that reads settings from an INI/CFG file.

    This loader reads configuration from a specified section in an INI-style
    configuration file.

    Args:
        filename (str): Path to the .ini/.cfg file.
        section (str): Section name inside the config file. Defaults to "settings".
        keyfmt (callable): Optional function to pre-format variable names.

    Raises:
        InvalidConfigurationFile: If the file is not a valid INI file.
        MissingSettingsSection: If the specified section is not found in the file.
    """

    def __init__(self, filename, section="settings", keyfmt=lambda x: x):
        self.filename = filename
        self.section = section
        self.keyfmt = keyfmt
        self.parser = ConfigParser(allow_no_value=True)
        self._initialized = False

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.filename}")'

    def _parse(self):
        """
        Parse the INI file if not already parsed.

        Raises:
            InvalidConfigurationFile: If the file is not a valid INI file.
            MissingSettingsSection: If the specified section is not found.
        """
        if self._initialized:
            return

        with open(self.filename, encoding="utf-8") as inifile:
            try:
                self.parser.read_file(inifile)
            except (UnicodeDecodeError, MissingSectionHeaderError) as err:
                raise InvalidConfigurationFile() from err

        if not self.parser.has_section(self.section):
            raise MissingSettingsSection(
                f"Missing [{self.section}] section in {self.filename}"
            )

        self._initialized = True

    def check(self):
        """
        Verify if the INI file exists and is valid.

        Returns:
            bool: True if the file exists and is valid, False otherwise.
        """
        try:
            self._parse()
        except (FileNotFoundError, InvalidConfigurationFile, MissingSettingsSection):
            return False

        return super().check()

    def __contains__(self, item):
        """Check if a configuration key exists in the INI file section."""
        if not self.check():
            return False

        return self.parser.has_option(self.section, self.keyfmt(item))

    def __getitem__(self, item):
        """
        Retrieve a configuration value from the INI file section.

        Args:
            item (str): The configuration key to retrieve.

        Returns:
            str: The configuration value.

        Raises:
            KeyError: If the key doesn't exist in the section.
        """
        if not self.check():
            raise KeyError(f"{item}")

        try:
            return self.parser.get(self.section, self.keyfmt(item))
        except NoOptionError as err:
            raise KeyError(f"{item}") from err

    def reset(self):
        """Reset the parser's initialization state."""
        self._initialized = False


class Environment(AbstractConfigurationLoader):
    """
    Configuration loader that reads settings from environment variables.

    This loader retrieves configuration values from the system's environment
    variables (os.environ), optionally transforming the keys using a formatting
    function.

    Args:
        keyfmt (callable): Optional function to pre-format variable names.
                          Defaults to EnvPrefix() which converts keys to uppercase.

    Example:
        >>> env = Environment(keyfmt=EnvPrefix("MYAPP_"))
        >>> os.environ["MYAPP_DEBUG"] = "true"
        >>> "debug" in env  # True
        >>> env["debug"]  # "true"
    """

    def __init__(self, keyfmt=EnvPrefix()):
        """
        :param function keyfmt: A function to pre-format variable names.
        """
        self.keyfmt = keyfmt

    def __repr__(self):
        return f"{self.__class__.__name__}(keyfmt={self.keyfmt})"

    def __contains__(self, item):
        """Check if an environment variable exists for the given key."""
        return self.keyfmt(item) in os.environ

    def __getitem__(self, item):
        """
        Retrieve a configuration value from environment variables.

        Args:
            item (str): The configuration key to retrieve.

        Returns:
            str: The environment variable value.

        Raises:
            KeyError: If the environment variable doesn't exist.
        """
        return os.environ[self.keyfmt(item)]


class EnvFile(AbstractConfigurationLoader):
    """
    Configuration loader that reads settings from a .env file.

    This loader reads configuration values from a file in environment variable
    format (KEY=value).

    Args:
        filename (str): Path to the .env file. Defaults to ".env".
        keyfmt (callable): Optional function to pre-format variable names.
                          Defaults to EnvPrefix() which converts keys to uppercase.

    Example:
        >>> env = EnvFile(".env", keyfmt=EnvPrefix("MYAPP_"))
        >>> # With .env containing: DEBUG=true
        >>> "debug" in env  # True
        >>> env["debug"]  # "true"
    """

    def __init__(self, filename=".env", keyfmt=EnvPrefix()):
        self.filename = filename
        self.keyfmt = keyfmt
        self.configs = None

    def __repr__(self):
        return f'{self.__class__.__name__}("{self.filename}")'

    def _parse(self):
        """
        Parse the .env file if not already parsed.

        Raises:
            FileNotFoundError: If the file doesn't exist or can't be read.
        """
        if self.configs is not None:
            return

        self.configs = {}
        with open(self.filename, encoding="utf-8") as envfile:
            self.configs.update(EnvFileParser(envfile).parse_config())

    def check(self):
        """
        Verify if the .env file exists and is valid.

        Returns:
            bool: True if the file exists and is valid, False otherwise.
        """
        if not os.path.isfile(self.filename):
            return False

        try:
            self._parse()
        except FileNotFoundError:
            return False

        return super().check()

    def __contains__(self, item):
        """Check if a configuration key exists in the .env file."""
        if not self.check():
            return False

        return self.keyfmt(item) in self.configs

    def __getitem__(self, item):
        """
        Retrieve a configuration value from the .env file.

        Args:
            item (str): The configuration key to retrieve.

        Returns:
            str: The configuration value.

        Raises:
            KeyError: If the key doesn't exist in the file.
        """
        if not self.check():
            raise KeyError(f"{item}")

        return self.configs[self.keyfmt(item)]

    def reset(self):
        """Reset the parsed configuration cache."""
        self.configs = None


class RecursiveSearch(AbstractConfigurationLoader):
    """
    Configuration loader that recursively searches for configuration files.

    This loader looks for configuration files in the current directory and all parent
    directories up to a specified root path. It supports multiple file types and loaders.

    Args:
        starting_path (str, optional): The path to begin looking for configuration files.
        filetypes (tuple): Tuple of (pattern, loader_class) pairs defining which files
                          to look for and how to load them. Defaults to .env, .ini, and .cfg files.
        root_path (str): The path where the search will stop. Defaults to "/".

    Example:
        >>> search = RecursiveSearch("/home/user/project")
        >>> # Will look for .env, .ini, and .cfg files in:
        >>> # /home/user/project
        >>> # /home/user
        >>> # /home
        >>> # /
    """

    def __init__(
        self,
        starting_path=None,
        filetypes=((".env", EnvFile), (("*.ini", "*.cfg"), IniFile)),
        root_path="/",
    ):
        self.root_path = os.path.realpath(root_path)
        self._starting_path = self.root_path

        if starting_path:
            self.starting_path = starting_path

        self.filetypes = filetypes
        self._config_files = None

    @property
    def starting_path(self):
        """Get the current starting path for the search."""
        return self._starting_path

    @starting_path.setter
    def starting_path(self, path):
        """
        Set the starting path for the search.

        Args:
            path (str): The new starting path.

        Raises:
            InvalidPath: If the path is invalid or outside the root path.
        """
        if not path:
            raise InvalidPath("Invalid starting path")

        path = os.path.realpath(os.path.abspath(path))
        if not path.startswith(self.root_path):
            raise InvalidPath("Invalid root path given")
        self._starting_path = path

    @staticmethod
    def get_filenames(path, patterns):
        """
        Get all filenames in a directory matching the given patterns.

        Args:
            path (str): Directory to search in.
            patterns (str or tuple): Glob pattern(s) to match against.

        Returns:
            list: List of matching filenames.
        """
        filenames = []
        if isinstance(patterns, str):
            patterns = (patterns,)

        for pattern in patterns:
            filenames += glob(os.path.join(path, pattern))
        return filenames

    def _scan_path(self, path):
        """
        Scan a directory for configuration files.

        Args:
            path (str): Directory to scan.

        Returns:
            list: List of configuration loader instances for found files.
        """
        config_files = []

        for patterns, Loader in self.filetypes:
            for filename in self.get_filenames(path, patterns):
                try:
                    loader = Loader(filename=filename)
                    if not loader.check():
                        continue
                    config_files.append(loader)
                except InvalidConfigurationFile:
                    continue

        return config_files

    def _discover(self):
        """Discover all configuration files in the search path hierarchy."""
        self._config_files = []

        path = self.starting_path
        while True:
            if os.path.isdir(path):
                self._config_files += self._scan_path(path)

            if path == self.root_path:
                break

            path = os.path.dirname(path)

    @property
    def config_files(self):
        """
        Get all discovered configuration files.

        Returns:
            list: List of configuration loader instances.
        """
        if self._config_files is None:
            self._discover()

        return self._config_files

    def __contains__(self, item):
        """Check if a configuration key exists in any of the discovered files."""
        for config_file in self.config_files:
            if item in config_file:
                return True
        return False

    def __getitem__(self, item):
        """
        Retrieve a configuration value from the first file that contains it.

        Args:
            item (str): The configuration key to retrieve.

        Returns:
            str: The configuration value.

        Raises:
            KeyError: If the key doesn't exist in any configuration file.
        """
        for config_file in self.config_files:
            try:
                return config_file[item]
            except KeyError:
                continue

        raise KeyError(f"{item}")

    def __repr__(self):
        return f"{self.__class__.__name__}(root_path={self.root_path})"

    def reset(self):
        """Reset the discovered configuration files cache."""
        self._config_files = None


class Dict(AbstractConfigurationLoader):
    """
    Configuration loader that uses a dictionary as the configuration source.

    This loader is useful for providing hardcoded default values or for testing.

    Args:
        values_mapping (dict): A dictionary of configuration key-value pairs.

    Example:
        >>> config = Dict({"debug": "true", "port": "8000"})
        >>> "debug" in config  # True
        >>> config["port"]  # "8000"
    """

    def __init__(self, values_mapping):
        self.values_mapping = values_mapping

    def __repr__(self):
        return f"{self.__class__.__name__}({self.values_mapping})"

    def __contains__(self, item):
        """Check if a configuration key exists in the dictionary."""
        return item in self.values_mapping

    def __getitem__(self, item):
        """
        Retrieve a configuration value from the dictionary.

        Args:
            item (str): The configuration key to retrieve.

        Returns:
            The configuration value.

        Raises:
            KeyError: If the key doesn't exist in the dictionary.
        """
        return self.values_mapping[item]


class _Value(AbstractConfigurationLoader):
    """
    Internal configuration loader for handling single values.

    This is an internal class used for managing individual configuration values
    within the configuration system.

    Args:
        values_mapping (dict): A dictionary containing the configuration value.
    """

    def __init__(self, values_mapping):
        self.values_mapping = values_mapping

    def __repr__(self):
        return f"{self.__class__.__name__}({self.values_mapping})"

    def __contains__(self, item):
        """Check if the value exists for the given key."""
        return item in self.values_mapping

    def __getitem__(self, item):
        """Retrieve the value for the given key."""
        return self.values_mapping[item]

    def getitem(self, config, item, value=NOT_SET, **kwargs):
        """
        Get or set a configuration value.

        Args:
            config: The configuration object.
            item (str): The configuration key.
            value: The value to set (optional).
            **kwargs: Additional arguments.

        Returns:
            The configuration value.
        """
        if value is not NOT_SET:
            self.values_mapping = value
        return self.__getitem__(item)


class _Value22(AbstractConfigurationLoader):
    """
    Alternative internal configuration loader for handling single values.

    This is an internal class used for managing individual configuration values
    with slightly different behavior than _Value.

    Args:
        values_mapping (dict): A dictionary containing the configuration value.
    """

    def __init__(self, values_mapping):
        self.values_mapping = values_mapping

    def __repr__(self):
        return f"{self.__class__.__name__}({self.values_mapping})"

    def __contains__(self, item):
        """Check if the value exists for the given key."""
        return item in self.values_mapping

    def __getitem__(self, item):
        """Retrieve the value for the given key."""
        return self.values_mapping[item]

    def getitem(self, config, item, value=NOT_SET, **kwargs):
        """
        Get or set a configuration value.

        Args:
            config: The configuration object.
            item (str): The configuration key.
            value: The value to set (optional).
            **kwargs: Additional arguments.

        Returns:
            The value parameter if provided, otherwise the stored value.
        """
        return value
