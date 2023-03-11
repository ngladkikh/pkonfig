import configparser
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO, Any, Literal, Mapping, Tuple, Union

from pkonfig.base import BaseStorage, InternalStorage, Storage
from pkonfig.storage.base import DEFAULT_DELIMITER, DEFAULT_PREFIX, EnvMixin

MODE = Literal["r", "rb"]


class BaseFileStorage(ABC):
    file: Union[Path, str]
    mode: MODE = "r"
    missing_ok: bool = False

    def __init__(
        self,
        file: Union[Path, str],
        missing_ok: bool = False,
    ) -> None:
        self.file = file
        self.missing_ok = missing_ok
        self.file_data: Mapping = self.load()

    def load(self) -> Mapping:
        try:
            with open(  # pylint: disable=unspecified-encoding
                self.file, self.mode
            ) as fh:
                return self.load_file_content(fh)
        except FileNotFoundError:
            if self.missing_ok:
                return {}
            raise

    @abstractmethod
    def load_file_content(self, handler: IO) -> Mapping:
        pass

    def __len__(self) -> int:
        return len(self.file_data)


class DotEnv(BaseFileStorage, BaseStorage):
    def __init__(
        self,
        file: Union[Path, str],
        delimiter=DEFAULT_DELIMITER,
        prefix=DEFAULT_PREFIX,
        missing_ok: bool = False,
        **defaults,
    ):
        self.prefix = prefix + delimiter if prefix else ""
        self.delimiter = delimiter
        super().__init__(file, missing_ok)
        self.env_helper = EnvMixin(delimiter, prefix)
        self.defaults = Storage(defaults)

    def load_file_content(self, handler: IO) -> Mapping:
        res = {}
        for line in filter(self.filter, handler.readlines()):
            key, value = self.split(line)
            res[key] = value
        return res

    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        str_key = self.env_helper.to_key(key)
        upper_str_key = str_key.upper()
        if upper_str_key in self.file_data:
            return self.file_data[upper_str_key]

        if str_key in self.file_data:
            return self.file_data[str_key]

        return self.defaults[key]

    @staticmethod
    def split(param_line: str) -> Tuple[str, str]:
        """Splits string on key and value, removes prefix and spaces"""
        key: str
        key, value = param_line.split("=", maxsplit=1)
        return key.strip(), value.strip()

    @staticmethod
    def filter(param_line: str) -> bool:
        return len(param_line) > 2 and (not param_line.startswith(("#", "//")))


class FileStorage(BaseStorage, BaseFileStorage, ABC):
    def __init__(
        self,
        file: Union[Path, str],
        missing_ok: bool = False,
        **defaults,
    ) -> None:
        super().__init__(file, missing_ok)
        self.internal_storage = Storage(self.file_data, defaults)

    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        return self.internal_storage[key]

    @abstractmethod
    def load_file_content(self, handler: IO) -> Mapping:
        pass

    def __len__(self) -> int:
        return len(self.internal_storage)


class Json(FileStorage):
    def load_file_content(self, handler: IO) -> dict:
        return json.load(handler)


class Ini(FileStorage):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        file: Union[Path, str],
        missing_ok=False,
        allow_no_value=False,
        delimiters=("=", ":"),
        comment_prefixes=("#", ";"),
        inline_comment_prefixes=None,
        strict=True,
        empty_lines_in_values=True,
        default_section=configparser.DEFAULTSECT,
        **defaults,
    ):
        self.parser = configparser.ConfigParser(
            allow_no_value=allow_no_value,
            delimiters=delimiters,
            comment_prefixes=comment_prefixes,
            inline_comment_prefixes=inline_comment_prefixes,
            strict=strict,
            empty_lines_in_values=empty_lines_in_values,
            default_section=default_section,
        )
        super().__init__(file=file, missing_ok=missing_ok, **defaults)

    def load_file_content(self, handler: IO) -> InternalStorage:
        self.parser.read_string(handler.read())
        return self.parser  # type: ignore
