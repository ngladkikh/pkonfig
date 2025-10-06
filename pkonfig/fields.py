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
    Dict,
    Generic,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union,
    overload,
)

from pkonfig.config import Config
from pkonfig.descriptor_helper import _Descriptor
from pkonfig.errors import ConfigError, ConfigTypeError, ConfigValueNotFoundError
from pkonfig.storage.base import InternalKey

NOT_SET = "NOT_SET"
T = TypeVar("T")


class Field(Generic[T], _Descriptor[T], ABC):
    """Base config attribute descriptor.

    Field is a data descriptor used as a class attribute of a Config subclass.
    On first access it retrieves a raw value from the attached storage, casts it
    to the target Python type and validates it. The result is cached per-field key.

    Parameters
    ----------
    default : Any, optional
        Default value if the key is not found in storage. If left as NOT_SET
        a ConfigValueNotFoundError will be raised on access. If default is None
        the field becomes nullable.
    alias : str, optional
        Name to use in storage instead of the attribute name, by default "".
    nullable : bool, optional
        Whether None is accepted as a value, by default False.
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
        self._cache: Dict[InternalKey, T] = {}

    def __set_name__(self, _: Type[Config], name: str) -> None:
        self.alias = self.alias or name

    def __set__(self, instance: Config, value: Any) -> None:
        path = self._get_path(instance)
        logging.warning(
            "Setting %s config value in runtime, proceed with caution",
            self.key_to_name(path),
        )
        try:
            value = self._cast(value)
            self._validate(value)
        except ConfigError:
            raise
        except Exception as exc:
            raise ConfigTypeError(
                f"set {self.key_to_name(path)} to {value} not allowed"
            ) from exc
        self._cache[path] = value

    def _get_path(self, config: Config) -> InternalKey:
        return *config.get_roo_path(), self.alias

    @overload
    def __get__(self, instance: None, owner: Type[Config]) -> "Field[T]": ...

    @overload
    def __get__(self, instance: "Config", owner: Type[Config]) -> T: ...

    def __get__(
        self, instance: Optional["Config"], owner: Optional[Type["Config"]] = None
    ) -> Union[T, "Field[T]"]:
        if instance is None:
            # Accessed through the class: return the descriptor itself
            return self
        path = self._get_path(instance)
        if path not in self._cache:
            raw_value = instance.get_storage().get(path, self.default)
            try:
                value = self._cast(raw_value)
                self._validate(value)
            except ConfigError:
                raise
            except Exception as exc:
                raise ConfigTypeError(f"{self.key_to_name(path)} config error") from exc
            self._cache[path] = value
        return self._cache[path]

    @staticmethod
    def key_to_name(key: InternalKey) -> str:
        return ".".join(key)

    def _cast(self, value: Any) -> T:
        if value in (NOT_SET, None):
            return value
        return self.cast(value)

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def _validate(self, value: Any) -> None:
        if value is None and not self.nullable:
            raise ValueError("Not nullable")
        if value is NOT_SET:
            raise ConfigValueNotFoundError("Not set")
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
    def __init__(  # pylint: disable=too-many-positional-arguments
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
