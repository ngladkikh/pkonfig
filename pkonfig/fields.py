import logging
from abc import abstractmethod
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Optional, Sequence, Type, TypeVar, Union

from pkonfig.config import Config
from pkonfig.errors import ConfigTypeError, ConfigValueNotFoundError
from pkonfig.storage.base import InternalKey

NOT_SET = "NOT_SET"
T = TypeVar("T")


class Field(Generic[T]):
    """Base config attribute descriptor"""

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.default: Union[T, object] = default
        self.alias: str = alias
        self.nullable = default is None or nullable
        self._cache: T = NOT_SET    # type:ignore
        self._path: InternalKey = tuple()

    @property
    def error_name(self) -> str:
        return ".".join(self._path)

    def __set_name__(self, _: Type[Config], name: str) -> None:
        self.alias = self.alias or name

    def __set__(self, instance: Config, value) -> None:
        value = self._cast(value)
        self._validate(value)
        self._cache = value

    def __get__(self, instance: Config, _=None) -> T:
        if self._cache is NOT_SET:
            self._cache = self.get_from_storage(instance)
        return self._cache

    def get_from_storage(self, instance: Config) -> T:
        value = self._get_from_storage(instance)
        if value is None and not self.nullable:
            raise ConfigTypeError(f"Field {self.error_name} is not nullable")
        if value is not None:
            value = self._cast(value)
            self._validate(value)
        return value

    def _get_from_storage(self, instance: Config) -> Any:
        storage = instance.get_storage()
        self._path = (*instance.get_roo_path(), self.alias)
        if self._path in storage:
            return storage[self._path]
        if self.default is NOT_SET:
            raise ConfigValueNotFoundError(self.error_name)
        return self.default

    def _cast(self, value: Any) -> T:
        try:
            return self.cast(value)
        except (ValueError, TypeError) as exc:
            raise ConfigTypeError(f"{self.error_name} failed to cast {value}") from exc

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def _validate(self, value: Any) -> None:
        try:
            return self.validate(value)
        except TypeError as exc:
            raise ConfigTypeError(f"{self.error_name}: {value} invalid") from exc

    def validate(self, value: Any) -> None:
        pass


class Bool(Field[bool]):
    def cast(self, value) -> bool:
        return bool(value)


class Int(Field[int]):
    def cast(self, value) -> int:
        return int(value)


class Float(Field[float]):
    def cast(self, value) -> float:
        return float(value)


class DecimalField(Field[Decimal]):
    def cast(self, value) -> Decimal:
        return Decimal(float(value))


class Str(Field[str]):
    def cast(self, value) -> str:
        return str(value)


class Byte(Field):
    def cast(self, value) -> bytes:
        return bytes(value)


class ByteArray(Field):
    def cast(self, value) -> bytearray:
        return bytearray(value)


class PathField(Field[Path]):
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
    def validate(self, value):
        if (value.exists() and value.is_file()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a file")


class Folder(PathField):
    def validate(self, value):
        if (value.exists() and value.is_dir()) or self.missing_ok:
            return
        raise TypeError(f"{value.absolute()} is not a directory")


EnumT = TypeVar("EnumT", bound=Enum)


class EnumField(Field[EnumT], Generic[EnumT]):
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


class DebugFlag(Field):
    def cast(self, value: str) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            value = str(value)
        return value.lower() in ("true", "yes", "y", "1", "+")
