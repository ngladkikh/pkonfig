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
)

from pkonfig.config import Config
from pkonfig.errors import ConfigError, ConfigTypeError, ConfigValueNotFoundError
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

    def __get__(self, instance: Config, _=None) -> T:
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
    def cast(self, value: str) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, int):
            value = str(value)
        return value.lower() in ("true", "yes", "y", "1", "+")


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


class Byte(Field[bytes]):
    def cast(self, value) -> bytes:
        return bytes(value)


class ByteArray(Field[bytearray]):
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
