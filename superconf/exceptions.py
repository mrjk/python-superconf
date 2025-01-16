"Superconf Exceptions"


class ConfigurationException(Exception):
    "General error"


class InvalidConfigurationFile(ConfigurationException):
    "Invalid configuration File"


class MissingSettingsSection(InvalidConfigurationFile):
    "Missing section setting"


class InvalidPath(ConfigurationException):
    "Configuration Exception"


class InvalidCastConfiguration(ConfigurationException):
    "Raised when an invalid cast configuration is found"


class CastValueFailure(ConfigurationException):
    "Raised when a value can't be casted"


class UndeclaredField(ConfigurationException):
    "Raised when querrying unexisting field"


class UnknownExtraField(ConfigurationException):
    "Raised when trying to set value of undefined field. Enable extra_fields=True to disable"


class UnknownSetting(ConfigurationException):
    "Raised when an unexpected field is met. Enable extra_fields=True to disable this error"
