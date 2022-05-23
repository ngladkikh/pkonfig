import json
import os
from abc import ABC, abstractmethod
from collections import UserDict
from pathlib import Path
from typing import Any, Dict, List, Tuple, IO, Union
import configparser

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal   # type:ignore


MODE = Literal["r", "rb"]


class AbstractStorage(UserDict, ABC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load()

    @abstractmethod
    def load(self) -> None:
        """Load storage from source to cache"""
        pass


class BaseFileStorage(AbstractStorage, ABC):
    file: Union[Path, str]
    mode: MODE = "r"
    missing_ok: bool = False

    def __init__(self, file: Union[Path, str], missing_ok: bool = False, **kwargs):
        self.file = file
        self.missing_ok = missing_ok
        super().__init__(**kwargs)

    def load(self) -> None:
        try:
            with open(self.file, self.mode) as fh:
                self.load_file_content(fh)
        except FileNotFoundError:
            if not self.missing_ok:
                raise

    @abstractmethod
    def load_file_content(self, handler: IO) -> None:
        pass


class PlainStructureParserMixin:
    delimiter: str = "_"
    prefix: str = "APP"
    data: Dict

    def save_key_value(self, key: str, value: Any) -> None:
        if self.prefix is None or key.startswith(self.prefix):
            levels, leaf = self.split_and_normalize(key)
            storage = self.leaf_level_storage(levels)
            storage[leaf] = value

    def leaf_level_storage(self, levels: List[str]) -> Dict:
        storage = self.data
        for level in levels:
            if level not in storage:
                storage[level] = {}
            storage = storage[level]
        return storage

    def split_and_normalize(self, key: str) -> Tuple[List[str], str]:
        parts = key.split(self.delimiter)
        normalized_parts = [p.lower() for p in filter(self.is_key_part, parts)]
        leaf = normalized_parts.pop()
        return normalized_parts, leaf

    def is_key_part(self, key: str) -> bool:
        if key:
            if self.prefix:
                return key != self.prefix
            return True
        return False


class Env(PlainStructureParserMixin, AbstractStorage):
    def __init__(self, delimiter="_", prefix="APP", **kwargs):
        self.delimiter = delimiter
        self.prefix = prefix
        super(Env, self).__init__(**kwargs)

    def load(self) -> None:
        for key, value in os.environ.items():
            self.save_key_value(key, value)


class DotEnv(PlainStructureParserMixin, BaseFileStorage):
    def __init__(
        self,
        file: Union[Path, str],
        prefix="APP",
        delimiter="_",
        missing_ok: bool = False,
        **kwargs
    ):
        self.delimiter = delimiter
        self.prefix = prefix
        super().__init__(file=file, missing_ok=missing_ok, **kwargs)

    def load_file_content(self, handler: IO) -> None:
        for line in filter(self.filter, handler.readlines()):
            key, value = self.split(line)
            self.save_key_value(key, value)

    @staticmethod
    def split(param_line: str) -> Tuple[str, str]:
        key, value = param_line.split("=", maxsplit=1)
        return key.strip(), value.strip()

    @staticmethod
    def filter(param_line: str) -> bool:
        return len(param_line) > 2 and (not param_line.startswith(("#", "//")))


class Json(BaseFileStorage):
    def load_file_content(self, handler: IO) -> None:
        self.data.update(json.load(handler))


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

    def load_file_content(self, handler: IO) -> None:
        self.parser.read_string(handler.read())
        self.data.update(self.parser)
