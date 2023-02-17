import json
import os
from abc import ABC, abstractmethod, ABCMeta
from pathlib import Path
from typing import Tuple, IO, Union, Any
import configparser

from base import Storage, DEFAULT_DELIMITER

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal   # type:ignore


MODE = Literal["r", "rb"]
DEFAULT_PREFIX = "APP"


class AbstractStorage(Storage, metaclass=ABCMeta):

    def __init__(self, delimiter: str = DEFAULT_DELIMITER, **kwargs) -> None:
        mapping = kwargs
        mapping.update(self.load())
        super().__init__(multilevel_mapping=mapping, delimiter=delimiter)

    @abstractmethod
    def load(self) -> dict:
        """Load storage from source to cache"""
        pass


class BaseFileStorage(AbstractStorage, ABC):
    file: Union[Path, str]
    mode: MODE = "r"
    missing_ok: bool = False

    def __init__(
        self,
        file: Union[Path, str],
        missing_ok: bool = False,
        delimiter: str = DEFAULT_DELIMITER,
        **kwargs
    ) -> None:
        self.file = file
        self.missing_ok = missing_ok
        super().__init__(delimiter=delimiter, **kwargs)

    def load(self) -> dict:
        try:
            with open(self.file, self.mode) as fh:
                return self.load_file_content(fh)
        except FileNotFoundError:
            if self.missing_ok:
                return {}
            raise

    @abstractmethod
    def load_file_content(self, handler: IO) -> dict[str, Any]:
        pass


class Env(AbstractStorage):
    def __init__(
        self,
        delimiter=DEFAULT_DELIMITER,
        prefix=DEFAULT_PREFIX,
        **kwargs
    ) -> None:
        self.prefix = prefix + delimiter if prefix else ""
        super().__init__(delimiter=delimiter, **kwargs)

    def load(self) -> dict:
        res = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                res[key.replace(self.prefix, "").upper()] = value
        return res


class DotEnv(BaseFileStorage):
    def __init__(
        self,
        file: Union[Path, str],
        delimiter=DEFAULT_DELIMITER,
        prefix=DEFAULT_PREFIX,
        missing_ok: bool = False,
        **kwargs
    ):
        self.prefix = prefix + delimiter if prefix else ""
        super().__init__(
            file=file,
            missing_ok=missing_ok,
            delimiter=delimiter,
            **kwargs,
        )

    def load_file_content(self, handler: IO) -> dict[str, Any]:
        res = {}
        for line in filter(self.filter, handler.readlines()):
            key, value = self.split(line)
            if key.startswith(self.prefix):
                res[key.replace(self.prefix, "")] = value
        return res

    @staticmethod
    def split(param_line: str) -> Tuple[str, str]:
        """Splits string on key and value, removes prefix and spaces"""
        key: str
        key, value = param_line.split("=", maxsplit=1)
        return key.strip(), value.strip()

    @staticmethod
    def filter(param_line: str) -> bool:
        return len(param_line) > 2 and (not param_line.startswith(("#", "//")))


class Json(BaseFileStorage):
    def load_file_content(self, handler: IO) -> dict[str, Any]:
        return json.load(handler)


class Ini(BaseFileStorage):
    def __init__(
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
        **kwargs
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
        super().__init__(file=file, missing_ok=missing_ok, **kwargs)

    def load_file_content(self, handler: IO) -> dict[str, Any]:
        self.parser.read_string(handler.read())
        return self.parser
