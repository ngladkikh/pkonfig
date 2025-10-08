class ConfigError(Exception):
    """Configuration error"""


class ConfigValueNotFoundError(ConfigError):
    """Failed to find value in a given storage (s)"""


class ConfigTypeError(ConfigError):
    """Value has the wrong type"""


class NullTypeError(ConfigError):
    """Non nullable value is None"""
