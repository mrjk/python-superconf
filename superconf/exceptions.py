"""Superconf exceptions

Provide generic exceptions
"""


class ConfigurationException(Exception):
    pass


class InvalidConfigurationFile(ConfigurationException):
    pass


class MissingSettingsSection(InvalidConfigurationFile):
    pass


class InvalidPath(ConfigurationException):
    pass


class UnknownConfiguration(ConfigurationException):
    pass


class InvalidConfiguration(ConfigurationException):
    pass


# Developper errors
# ----------------


class InvalidValueType(ConfigurationException):
    "Returned when a value does not fit the expected type"
    pass


class InvalidContainerType(ConfigurationException):
    pass


class InvalidContainerDefault(ConfigurationException):
    pass
