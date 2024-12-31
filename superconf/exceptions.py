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
    pass


class InvalidContainerType(ConfigurationException):
    pass


class InvalidContainerDefault(ConfigurationException):
    pass
