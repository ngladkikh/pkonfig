from importlib import metadata as _metadata
from pathlib import Path

from pkonfig.config import Config
from pkonfig.errors import ConfigError, ConfigTypeError, ConfigValueNotFoundError
from pkonfig.fields import (
    Bool,
    Byte,
    ByteArray,
    Choice,
    DecimalField,
    EnumField,
    Field,
    File,
    Float,
    Folder,
    Int,
    ListField,
    LogLevel,
    PathField,
    Str,
)
from pkonfig.storage import *

# Expose package version for documentation and consumers
try:
    __version__ = _metadata.version("pkonfig")
except _metadata.PackageNotFoundError:  # pragma: no cover - not in an installed context
    __version__ = "0.0.0"

Config.register_type_factory(str, Str)
Config.register_type_factory(int, Int)
Config.register_type_factory(float, Float)
Config.register_type_factory(bool, Bool)
Config.register_type_factory(Path, PathField)

__all__ = [
    "Config",
    "ConfigError",
    "ConfigTypeError",
    "ConfigValueNotFoundError",
    "Bool",
    "Byte",
    "ByteArray",
    "Choice",
    "DecimalField",
    "DictStorage",
    "EnumField",
    "Field",
    "File",
    "Float",
    "Folder",
    "Int",
    "ListField",
    "LogLevel",
    "PathField",
    "Str",
    "__version__",
]
