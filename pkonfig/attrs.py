"""
Attrs-based implementation of Config.

This module provides an alternative implementation of the Config class and fields
using attrs instead of descriptors. This implementation is significantly faster
for field access operations, but may have some limitations compared to the
descriptor-based implementation.

Example usage:
    from pkonfig.attrs import Config, Str, Int, Bool

    class AppConfig(Config):
        name = Str("DefaultName")
        debug = Bool(False)
        port = Int(8000)
"""
from pkonfig.attrs_config import (
    AttrsConfig as Config,
    Str,
    Int,
    Float,
    Bool,
    Decimal,
    Path,
    File,
    Folder,
    Enum,
    LogLevel,
    Choice,
)

__all__ = [
    "Config",
    "Str",
    "Int",
    "Float",
    "Bool",
    "Decimal",
    "Path",
    "File",
    "Folder",
    "Enum",
    "LogLevel",
    "Choice",
]