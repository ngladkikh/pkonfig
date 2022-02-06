import os
from abc import abstractmethod
from collections import UserDict
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Tuple


class PlainStructureStorage(UserDict):
    def __init__(self, prefix="APP", delimiter="_", **kwargs):
        super().__init__(**kwargs)
        self.delimiter = delimiter
        prefix += delimiter
        for key in filter(self.app_keys(prefix), self.plain_raw_storage):
            self.set_multilevel_value(key, self.plain_raw_storage[key])

    def set_multilevel_value(self, key: str, value: str) -> None:
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
        _, *parts = key.split(self.delimiter)
        normalized_parts = [p.lower() for p in parts if p]
        leaf = normalized_parts.pop()
        return normalized_parts, leaf

    @staticmethod
    def normalize(key) -> str:
        if not key:
            raise ValueError()
        return key.lower()

    @staticmethod
    def app_keys(prefix: str) -> Callable[[str], bool]:
        return lambda x: x.startswith(prefix)

    @property
    @abstractmethod
    def plain_raw_storage(self) -> Mapping[str, str]:
        return os.environ


class EnvConfigStorage(PlainStructureStorage):
    @property
    def plain_raw_storage(self) -> Mapping[str, str]:
        return os.environ


class EnvFileConfigStorage(PlainStructureStorage):

    def __init__(
        self,
        prefix="APP",
        delimiter="_",
        file: Path = Path(".env"),
        **kwargs
    ):
        self.file_path = file
        self.__storage = None
        super().__init__(prefix=prefix, delimiter=delimiter, **kwargs)

    @property
    def plain_raw_storage(self) -> Mapping[str, str]:
        if self.__storage is None:
            self.__storage = self.read_file()
        return self.__storage

    def read_file(self):
        with open(self.file_path) as fh:
            raw_params = fh.readlines()
        return {
            key: value
            for key, value in map(self.split_, filter(self.filter_, raw_params))
        }

    @staticmethod
    def split_(param_line: str) -> Tuple[str, str]:
        key, value = param_line.split("=", maxsplit=2)
        return key.strip(), value.strip()

    @staticmethod
    def filter_(param_line: str) -> bool:
        return param_line and (not param_line.startswith(("#", "//")))
