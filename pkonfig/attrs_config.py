"""
Alternative implementation of Config using attrs for field validation.

This module provides an alternative implementation of the Config class and fields
using attrs instead of descriptors. This implementation is significantly faster
for field access operations, but may have some limitations compared to the
descriptor-based implementation.
"""
import logging
from abc import abstractmethod
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    ClassVar,
)
from collections import ChainMap

import attr

from pkonfig.errors import ConfigError, ConfigTypeError, ConfigValueNotFoundError
from pkonfig.storage.base import InternalKey

T = TypeVar("T")
NOT_SET = "NOT_SET"


def _get_path(config: "AttrsConfig", alias: str) -> InternalKey:
    return (*config._root_path, alias)


class FieldInfo(Generic[T]):
    """Field information for attrs-based config fields."""

    def __init__(
        self,
        default: Any = NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.default: Union[T, object] = default
        self.alias: str = alias
        self.nullable = default is None or nullable

    def cast(self, value: Any) -> T:
        """Cast the value to the appropriate type."""
        if value in (NOT_SET, None):
            return value
        return self._cast(value)

    @abstractmethod
    def _cast(self, value: Any) -> T:
        """Implement this method to cast the value to the appropriate type."""
        pass

    def validate(self, value: Any) -> None:
        """Validate the value."""
        if value is None and not self.nullable:
            raise ValueError("Not nullable")
        if value is NOT_SET:
            raise ConfigValueNotFoundError("Not set")


class StrInfo(FieldInfo[str]):
    """String field information."""

    def _cast(self, value) -> str:
        return str(value)


class IntInfo(FieldInfo[int]):
    """Integer field information."""

    def _cast(self, value) -> int:
        return int(value)


class FloatInfo(FieldInfo[float]):
    """Float field information."""

    def _cast(self, value) -> float:
        return float(value)


class BoolInfo(FieldInfo[bool]):
    """Boolean field information."""

    def _cast(self, value) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            value = str(value)
        return value.lower() in ("true", "yes", "y", "1", "+")


class DecimalInfo(FieldInfo[Decimal]):
    """Decimal field information."""

    def _cast(self, value) -> Decimal:
        return Decimal(float(value))


class PathInfo(FieldInfo[Path]):
    """Path field information."""

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
        missing_ok: bool = False,
    ):
        self.missing_ok = missing_ok
        super().__init__(default, alias, nullable)

    def _cast(self, value) -> Path:
        return Path(value)

    def validate(self, value: Path) -> None:
        super().validate(value)
        if not value.exists() and not self.missing_ok:
            raise FileNotFoundError(f"File {value.absolute()} not found")


class FileInfo(PathInfo):
    """File field information."""

    def validate(self, value: Path) -> None:
        super().validate(value)
        if (value.exists() and value.is_file()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a file")


class FolderInfo(PathInfo):
    """Folder field information."""

    def validate(self, value: Path) -> None:
        super().validate(value)
        if (value.exists() and value.is_dir()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a directory")


EnumT = TypeVar("EnumT", bound=Enum)


class EnumInfo(FieldInfo[EnumT], Generic[EnumT]):
    """Enum field information."""

    def __init__(
        self,
        enum_cls: Type[EnumT],
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.enum_cls = enum_cls
        super().__init__(default, alias, nullable)

    def _cast(self, value: str) -> EnumT:
        return self.enum_cls[value]


class LogLevelInfo(FieldInfo[int]):
    """Log level field information."""

    class Levels(Enum):
        NOTSET = logging.NOTSET
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = logging.CRITICAL

    def _cast(self, value: str) -> int:
        return self.Levels[value.upper()].value


class ChoiceInfo(FieldInfo[T], Generic[T]):
    """Choice field information."""

    def __init__(
        self,
        choices: Sequence[T],
        cast_function: Optional[Callable[[Any], T]] = None,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.choices = choices
        self.cast_function = cast_function
        super().__init__(default, alias, nullable)

    def _cast(self, value: T) -> T:
        if self.cast_function is not None:
            value = self.cast_function(value)
        return value

    def validate(self, value: Any) -> None:
        super().validate(value)
        if value not in self.choices:
            raise ConfigTypeError(f"'{value}' is not in {self.choices}")


# Field factory functions
def Str(default=NOT_SET, alias: str = "", nullable: bool = False) -> StrInfo:
    """Create a string field."""
    return StrInfo(default, alias, nullable)


def Int(default=NOT_SET, alias: str = "", nullable: bool = False) -> IntInfo:
    """Create an integer field."""
    return IntInfo(default, alias, nullable)


def Float(default=NOT_SET, alias: str = "", nullable: bool = False) -> FloatInfo:
    """Create a float field."""
    return FloatInfo(default, alias, nullable)


def Bool(default=NOT_SET, alias: str = "", nullable: bool = False) -> BoolInfo:
    """Create a boolean field."""
    return BoolInfo(default, alias, nullable)


def Decimal(default=NOT_SET, alias: str = "", nullable: bool = False) -> DecimalInfo:
    """Create a decimal field."""
    return DecimalInfo(default, alias, nullable)


def Path(
    default=NOT_SET, alias: str = "", nullable: bool = False, missing_ok: bool = False
) -> PathInfo:
    """Create a path field."""
    return PathInfo(default, alias, nullable, missing_ok)


def File(
    default=NOT_SET, alias: str = "", nullable: bool = False, missing_ok: bool = False
) -> FileInfo:
    """Create a file field."""
    return FileInfo(default, alias, nullable, missing_ok)


def Folder(
    default=NOT_SET, alias: str = "", nullable: bool = False, missing_ok: bool = False
) -> FolderInfo:
    """Create a folder field."""
    return FolderInfo(default, alias, nullable, missing_ok)


def Enum(
    enum_cls: Type[EnumT], default=NOT_SET, alias: str = "", nullable: bool = False
) -> EnumInfo[EnumT]:
    """Create an enum field."""
    return EnumInfo(enum_cls, default, alias, nullable)


def LogLevel(default=NOT_SET, alias: str = "", nullable: bool = False) -> LogLevelInfo:
    """Create a log level field."""
    return LogLevelInfo(default, alias, nullable)


def Choice(
    choices: Sequence[T],
    cast_function: Optional[Callable[[Any], T]] = None,
    default=NOT_SET,
    alias: str = "",
    nullable: bool = False,
) -> ChoiceInfo[T]:
    """Create a choice field."""
    return ChoiceInfo(choices, cast_function, default, alias, nullable)


@attr.s(auto_attribs=True)
class AttrsConfig:
    """Base config class using attrs for field validation."""

    _storage: ChainMap = attr.ib(factory=ChainMap)
    _alias: str = attr.ib(default="")
    _root_path: InternalKey = attr.ib(factory=tuple)
    _cache: Dict[str, Any] = attr.ib(factory=dict)
    _field_info: ClassVar[Dict[str, FieldInfo]] = {}

    def __attrs_post_init__(self):
        """Initialize the config after attrs initialization."""
        self._root_path = (self._alias,) if self._alias else tuple()
        self._register_field_info()
        self._register_inner_configs()
        if self._storage:
            self.check()

    def _register_field_info(self):
        """Register field information for all fields."""
        cls = self.__class__
        if not hasattr(cls, "_field_info"):
            cls._field_info = {}

        for name, attr_value in vars(cls).items():
            if isinstance(attr_value, FieldInfo):
                attr_value.alias = attr_value.alias or name
                cls._field_info[name] = attr_value

    def _register_inner_configs(self):
        """Register inner configs."""
        for name, config_attribute in self._inner_configs():
            config_attribute.set_storage(self.get_storage())
            config_attribute.set_alias(name)
            config_attribute.set_root_path(self.get_root_path())

    def _inner_configs(self):
        """Get inner configs."""
        for name, attribute in vars(self.__class__).items():
            if isinstance(attribute, AttrsConfig):
                yield name, attribute

    def check(self):
        """Check all config attributes."""
        for name in self._field_info:
            self._get_field_value(name)
        for _, inner_config in self._inner_configs():
            inner_config.check()

    def _get_field_value(self, name):
        """Get the value of a field."""
        if name in self._cache:
            return self._cache[name]

        field_info = self._field_info.get(name)
        if not field_info:
            return getattr(self, name)

        path = _get_path(self, field_info.alias)
        raw_value = self._storage.get(path, field_info.default)

        try:
            value = field_info.cast(raw_value)
            field_info.validate(value)
        except ConfigError:
            raise
        except Exception as exc:
            key_name = ".".join(path)
            raise ConfigTypeError(f"{key_name} config error") from exc

        self._cache[name] = value
        return value

    def set_alias(self, alias: str):
        """Set the alias for this config."""
        self._alias = self._alias or alias

    def set_root_path(self, root_path: InternalKey):
        """Set the root path for this config."""
        self._root_path = (*root_path, self._alias) if self._alias else root_path

    def get_root_path(self) -> InternalKey:
        """Get the root path for this config."""
        return self._root_path

    def get_storage(self) -> ChainMap:
        """Get the storage for this config."""
        return self._storage

    def set_storage(self, storage: ChainMap):
        """Set the storage for this config."""
        self._storage = storage


# Add property methods for each field
def _add_property_methods():
    """Add property methods for each field to AttrsConfig."""
    def make_getter(name):
        def getter(self):
            return self._get_field_value(name)
        return getter

    for name in dir(AttrsConfig):
        if name.startswith("_") or name in ("check", "set_alias", "set_root_path", "get_root_path", "get_storage", "set_storage"):
            continue
        setattr(AttrsConfig, name, property(make_getter(name)))


# Call _add_property_methods at module import time
_add_property_methods()