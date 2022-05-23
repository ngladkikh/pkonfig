import logging
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Generic, Optional, Sequence, Type, TypeVar

from pkonfig.base import NOT_SET, Field


class Bool(Field):
    def cast(self, value) -> bool:
        return bool(value)


class Int(Field):
    def cast(self, value) -> int:
        return int(value)


class Float(Field):
    def cast(self, value) -> float:
        return float(value)


class DecimalField(Field):
    def cast(self, value) -> Decimal:
        return Decimal(float(value))


class Str(Field):
    def cast(self, value) -> str:
        return str(value)


class Byte(Field):
    def cast(self, value) -> bytes:
        return bytes(value)


class ByteArray(Field):
    def cast(self, value) -> bytearray:
        return bytearray(value)


class PathField(Field):
    value: Path
    missing_ok: bool

    def __init__(self, default=NOT_SET, no_cache=False, missing_ok=False):
        self.missing_ok = missing_ok
        super().__init__(default, no_cache)

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


class EnumField(Field):
    def __init__(self, enum_cls: Type[Enum], default=NOT_SET, no_cache=False):
        self.enum_cls = enum_cls
        super().__init__(default, no_cache)

    def cast(self, value: str) -> Enum:
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
        return self.Levels[value.upper()].value


T = TypeVar("T")


class Choice(Field, Generic[T]):
    def __init__(
        self,
        choices: Sequence[T],
        cast_function: Optional[Callable[[Any], T]] = None,
        default=NOT_SET,
        no_cache=False,
    ):
        self.choices = choices
        self.cast_function = cast_function
        super().__init__(default, no_cache)

    def cast(self, value: T) -> T:
        if self.cast_function is not None:
            value = self.cast_function(value)
        return value

    def validate(self, value):
        if value not in self.choices:
            raise TypeError(f"'{value}' is not in {self.choices}")


class DebugFlag(Field):
    def cast(self, value: str) -> T:
        return value.lower() == "true"
