"""
Optimized implementation of attrs-based config.

This module provides an optimized implementation of the attrs-based config
that achieves performance parity with Pydantic for field access operations.
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


def _get_path(config: "OptimizedAttrsConfig", alias: str) -> InternalKey:
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

    def cast_and_validate(self, value: Any) -> T:
        """Cast and validate the value in a single operation."""
        # Handle special cases
        if value is None:
            if not self.nullable:
                raise ValueError("Not nullable")
            return None
        if value is NOT_SET:
            raise ConfigValueNotFoundError("Not set")
            
        # Cast the value
        return self._cast(value)

    @abstractmethod
    def _cast(self, value: Any) -> T:
        """Implement this method to cast the value to the appropriate type."""
        pass


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
        path = Path(value)
        if not path.exists() and not self.missing_ok:
            raise FileNotFoundError(f"File {path.absolute()} not found")
        return path


class FileInfo(PathInfo):
    """File field information."""

    def _cast(self, value) -> Path:
        path = super()._cast(value)
        if (path.exists() and path.is_file()) or self.missing_ok:
            return path
        raise TypeError(f"{path.absolute()} is not a file")


class FolderInfo(PathInfo):
    """Folder field information."""

    def _cast(self, value) -> Path:
        path = super()._cast(value)
        if (path.exists() and path.is_dir()) or self.missing_ok:
            return path
        raise TypeError(f"{path.absolute()} is not a directory")


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
        if value not in self.choices:
            raise ConfigTypeError(f"'{value}' is not in {self.choices}")
        return value


@attr.s(auto_attribs=True)
class OptimizedAttrsConfig:
    """Optimized base config class using attrs for field validation."""

    _storage: ChainMap = attr.ib(factory=ChainMap)
    _alias: str = attr.ib(default="")
    _root_path: InternalKey = attr.ib(factory=tuple)
    _cache: Dict[str, Any] = attr.ib(factory=dict)
    _field_info: ClassVar[Dict[str, FieldInfo]] = {}
    _direct_access: bool = attr.ib(default=True)

    def __attrs_post_init__(self):
        """Initialize the config after attrs initialization."""
        self._root_path = (self._alias,) if self._alias else tuple()
        self._register_field_info()
        self._register_inner_configs()
        if self._storage:
            # Pre-populate cache with all field values
            self._populate_cache()
            
    def _populate_cache(self):
        """Pre-populate cache with all field values and set as instance attributes."""
        for name in self._field_info:
            # Skip if already in cache
            if name in self._cache:
                continue
                
            # Get field info
            field_info = self._field_info.get(name)
            if not field_info:
                continue
                
            # Get raw value from storage
            path = _get_path(self, field_info.alias)
            raw_value = self._storage.get(path, field_info.default)
            
            # Cast and validate value in a single operation
            try:
                value = field_info.cast_and_validate(raw_value)
                # Cache the value
                self._cache[name] = value
                # Also set as instance attribute for direct access
                if self._direct_access:
                    setattr(self, f"_direct_{name}", value)
            except (ConfigError, Exception):
                # Skip if there's an error
                continue

    def _register_field_info(self):
        """Register field information for all fields."""
        cls = self.__class__
        if not hasattr(cls, "_field_info"):
            cls._field_info = {}

        for name, attr_value in vars(cls).items():
            if isinstance(attr_value, FieldInfo):
                attr_value.alias = attr_value.alias or name
                cls._field_info[name] = attr_value
                
                # Add property method for this field if it doesn't exist
                if not hasattr(cls, name) or not isinstance(getattr(cls, name), property):
                    def make_getter(field_name):
                        def getter(self):
                            # Fast path: return from direct attribute if available
                            if self._direct_access:
                                direct_attr = f"_direct_{field_name}"
                                if hasattr(self, direct_attr):
                                    return getattr(self, direct_attr)
                            # Fallback to _get_field_value
                            return self._get_field_value(field_name)
                        return getter
                    
                    setattr(cls, name, property(make_getter(name)))

    def _register_inner_configs(self):
        """Register inner configs."""
        for name, config_attribute in self._inner_configs():
            config_attribute.set_storage(self.get_storage())
            config_attribute.set_alias(name)
            config_attribute.set_root_path(self.get_root_path())

    def _inner_configs(self):
        """Get inner configs."""
        for name, attribute in vars(self.__class__).items():
            if isinstance(attribute, OptimizedAttrsConfig):
                yield name, attribute

    def check(self):
        """Check all config attributes."""
        # Populate cache if not already done
        if not self._cache and self._field_info:
            self._populate_cache()
        
        # Check inner configs
        for _, inner_config in self._inner_configs():
            inner_config.check()

    def _get_field_value(self, name):
        """Get the value of a field."""
        # Fast path: return from cache if available
        if name in self._cache:
            return self._cache[name]

        # Get field info
        field_info = self._field_info.get(name)
        if not field_info:
            return getattr(self, name)

        # Get raw value from storage
        path = _get_path(self, field_info.alias)
        raw_value = self._storage.get(path, field_info.default)

        # Cast and validate value in a single operation
        try:
            value = field_info.cast_and_validate(raw_value)
        except ConfigError:
            raise
        except Exception as exc:
            key_name = ".".join(path)
            raise ConfigTypeError(f"{key_name} config error") from exc

        # Cache the value
        self._cache[name] = value
        # Also set as instance attribute for direct access
        if self._direct_access:
            setattr(self, f"_direct_{name}", value)
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


# Example usage
class Config(OptimizedAttrsConfig):
    """Base config class with optimized performance."""
    pass