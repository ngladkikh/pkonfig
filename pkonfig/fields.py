"""Field descriptors used to declare configuration schema.

This module provides the Field base descriptor and concrete field types (Str, Int,
Bool, etc.) used inside Config subclasses. A Field reads a raw value from storage,
casts it to a Python type, validates it and caches the result.
"""

import logging
from abc import ABC, abstractmethod
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from pkonfig.base_config import BaseConfig
from pkonfig.descriptor_helper import _Descriptor
from pkonfig.errors import ConfigError, ConfigTypeError, NullTypeError
from pkonfig.storage.base import NOT_SET

T = TypeVar("T")


class Field(Generic[T], _Descriptor[T], ABC):
    """Base config attribute descriptor.

    Field is a data descriptor used as a class attribute of a Config subclass.
    On first access it retrieves a raw value from the attached storage, casts it
    to the target Python type and validates it. The result is cached a per-field key.

    Parameters
    ----------
    default : Any, optional
        Default value if the key is not found in storage. If left as NOT_SET,
        a ConfigValueNotFoundError will be raised on access. If the default is None,
        the field becomes nullable.
    alias : str, optional
        Name to use in storage instead of the attribute name, by default "".
    nullable : bool, optional
        Whether None is accepted as a value, by default, False.
    """

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.default: Union[T, object] = default
        self.alias: str = alias
        self.nullable = default is None or nullable

    def __set_name__(self, _: Type[BaseConfig], name: str) -> None:
        self.alias = self.alias or name

    def __set__(self, instance: BaseConfig, value: Any) -> None:
        path = ".".join(instance.internal_key(self.alias))
        logging.warning(
            "Setting %s config value in runtime, proceed with caution", path
        )
        try:
            value = self._cast(value)
            self.validate(value)
            instance[self.alias] = value
        except ConfigError:
            raise
        except Exception as exc:
            raise ConfigTypeError(f"set {path} to {value} not allowed") from exc

    @overload
    def __get__(self, instance: None, owner: Type[BaseConfig]) -> "Field[T]": ...

    @overload
    def __get__(self, instance: BaseConfig, owner: Type[BaseConfig]) -> T: ...

    def __get__(
        self, instance: Optional[BaseConfig], owner: Optional[Type[BaseConfig]] = None
    ) -> Union[T, "Field[T]"]:
        if instance is None:
            # Accessed through the class: return the descriptor itself
            return self
        return self.get(instance)

    def get(self, instance: BaseConfig) -> T:
        if self.default != NOT_SET:
            raw_value = instance.get(self.alias, self.default)
        else:
            raw_value = instance[self.alias]

        try:
            value = self._cast(raw_value)
            self._validate(value)
            return value
        except NullTypeError as exc:
            path = ".".join(instance.internal_key(self.alias))
            raise ConfigTypeError(
                f"{path} value is not nullable. received None."
            ) from exc
        except Exception as exc:
            path = ".".join(instance.internal_key(self.alias))
            raise ConfigTypeError(f"'{path}' validation error error") from exc

    def _cast(self, value: Any) -> T:
        if value in (NOT_SET, None):
            return value
        return self.cast(value)

    @abstractmethod
    def cast(self, value: Any) -> T:
        """Cast value to a Python type."""

    def _validate(self, value: Any) -> None:
        if value is None and not self.nullable:
            raise NullTypeError("Not nullable")
        return self.validate(value)

    def validate(self, value: Any) -> None:
        """Implement this method to validate value"""


class Bool(Field[bool]):
    """Boolean field that accepts typical truthy strings and ints (e.g. 'true', '1')."""

    def cast(self, value: str) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            value = str(value)
        return value.lower() in ("true", "yes", "y", "1", "+")


class Int(Field[int]):
    """Integer field."""

    def cast(self, value) -> int:
        return int(value)


class Float(Field[float]):
    """Floating point number field."""

    def cast(self, value) -> float:
        return float(value)


class DecimalField(Field[Decimal]):
    """Decimal field stored as Decimal."""

    def cast(self, value) -> Decimal:
        return Decimal(float(value))


class Str(Field[str]):
    """String field."""

    def cast(self, value) -> str:
        return str(value)


class Byte(Field[bytes]):
    """Bytes field (immutable)."""

    def cast(self, value) -> bytes:
        return bytes(value)


# Backwards/alternate name often used in docs/tests
class Bytes(Byte):
    """Alias for Byte field."""


class ByteArray(Field[bytearray]):
    """Mutable bytearray field."""

    def cast(self, value) -> bytearray:
        return bytearray(value)


class PathField(Field[Path]):
    """Filesystem path field.

    Parameters
    ----------
    missing_ok : bool
        If True, skip existence checks in validate().
    """

    value: Path
    missing_ok: bool

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
        missing_ok: bool = False,
    ):
        self.missing_ok = missing_ok
        super().__init__(default, alias, nullable)

    def cast(self, value) -> Path:
        return Path(value)

    def validate(self, value: Path) -> None:
        if not value.exists() and not self.missing_ok:
            raise FileNotFoundError(f"File {value.absolute()} not found")


class File(PathField):
    """File path field that validates the path points to a file."""

    def validate(self, value):
        if (value.exists() and value.is_file()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a file")


class Folder(PathField):
    """Directory path field that validates the path points to a folder."""

    def validate(self, value):
        if (value.exists() and value.is_dir()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a directory")


EnumT = TypeVar("EnumT", bound=Enum)


class EnumField(Field[EnumT], Generic[EnumT]):
    """Enum field that maps string names to an Enum value.

    Parameters
    ----------
    enum_cls : Type[Enum]
        Enum class to use for casting/validation.
    """

    def __init__(
        self,
        enum_cls: Type[EnumT],
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.enum_cls = enum_cls
        super().__init__(default, alias, nullable)

    def cast(self, value: str) -> EnumT:
        return self.enum_cls[value]


class LogLevel(Field):
    """Logging level field that accepts names like 'INFO', 'DEBUG', etc."""

    class Levels(Enum):
        NOTSET = logging.NOTSET
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = logging.CRITICAL

    def cast(self, value: str) -> int:
        return self.Levels[value.upper()].value  # type: ignore


class Choice(Field[T], Generic[T]):
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

    def cast(self, value: T) -> T:
        if self.cast_function is not None:
            value = self.cast_function(value)
        return value

    def validate(self, value):
        if value not in self.choices:
            raise ConfigTypeError(f"'{value}' is not in {self.choices}")


class ListField(Field[T], Generic[T]):
    """Field for parsing sequences from strings or iterables."""

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
        separator: str = ",",
        cast_function: Optional[Callable[[Any], T]] = str,  # type: ignore[assignment]
    ):
        super().__init__(default=default, alias=alias, nullable=nullable)
        self.separator = separator
        self.cast_function = cast_function

    def cast(self, value: Any) -> T:
        if isinstance(value, str):
            value = list(map(str.strip, value.split(self.separator)))
        value = list(map(self.cast_function, value))  # type: ignore[arg-type]
        return value
