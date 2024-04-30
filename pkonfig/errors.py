class ConfigError(Exception):
    """Configuration error"""


class ConfigValueNotFoundError(ConfigError):
    """Failed to find value in given storage(s)"""


class ConfigTypeError(ConfigError):
    """Value has wrong type"""
