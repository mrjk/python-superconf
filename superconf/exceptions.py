class ConfigurationException(Exception):
    pass


class InvalidConfigurationFile(ConfigurationException):
    pass


class MissingSettingsSection(InvalidConfigurationFile):
    pass


class InvalidPath(ConfigurationException):
    pass


class InvalidCastConfiguration(ConfigurationException):
    "Raised when an invalid cast configuration is found"


class CastValueFailure(ConfigurationException):
    "Raised when a value can't be casted"


class UndeclaredField(ConfigurationException):
    "Raised when querrying unexisting field"
    pass


class UnknownExtraField(ConfigurationException):
    "Raised when trying to set value of undefined field. Enable extra_fields=True to disable this error"
    pass


class UnknownSetting(ConfigurationException):
    "Raised when an unexpected field is met. Enable extra_fields=True to disable this error"
    pass
