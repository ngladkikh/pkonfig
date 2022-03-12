import logging
from enum import Enum
from pathlib import Path
from typing import Generic, Sequence, Type, TypeVar

from pkonfig.base import NOT_SET, TypedParameter


T = TypeVar("T")


class IntParam(TypedParameter):
    def cast(self, string_value) -> int:
        return int(string_value)


class FloatParam(TypedParameter):
    def cast(self, string_value) -> float:
        return float(string_value)


class StrParam(TypedParameter):
    def cast(self, string_value) -> str:
        return str(string_value)


class PathParam(TypedParameter):
    value: Path
    missing_ok: bool

    def __init__(self, default=NOT_SET, no_cache=False, missing_ok=False):
        self.missing_ok = missing_ok
        super().__init__(default, no_cache)

    def cast(self, string_value) -> Path:
        return Path(string_value)

    def validate(self, value: Path) -> None:
        if not value.exists() and not self.missing_ok:
            raise FileNotFoundError(f"File {value.absolute()} not found")


class File(PathParam):
    def validate(self, value):
        super().validate(value)
        if value.is_file():
            return
        raise TypeError(f"{value.absolute()} is not a file")


class Folder(PathParam):
    def validate(self, value):
        super().validate(value)
        if value.is_dir():
            return
        raise TypeError(f"{value.absolute()} is not a directory")


class EnumParam(TypedParameter):
    def __init__(self, enum_cls: Type[Enum], default=NOT_SET, no_cache=False):
        self.enum_cls = enum_cls
        super().__init__(default, no_cache)

    def cast(self, string_value: str) -> int:
        return self.enum_cls[string_value].value


class LogLevel(TypedParameter):
    class Levels(Enum):
        NOTSET = logging.NOTSET
        DEBUG = logging.DEBUG
        INFO = logging.INFO
        WARNING = logging.WARNING
        ERROR = logging.ERROR
        CRITICAL = logging.CRITICAL

    def cast(self, string_value: str) -> int:
        return self.Levels[string_value.upper()].value


class Choice(TypedParameter, Generic[T]):
    def __init__(
        self, choices: Sequence[T], default=NOT_SET, no_cache=False
    ):
        self.choices = choices
        super().__init__(default, no_cache)

    def cast(self, string_value: str) -> T:
        return string_value

    def validate(self, value):
        if value not in self.choices:
            raise TypeError(f"'{value}' is not in {self.choices}")
