import os
from abc import ABC, abstractmethod
from collections import UserDict
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Tuple, Union, get_type_hints

Values = Union[str, int, float]
ConfigStorage = Mapping[str, Any]


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


class TypedParameter(ABC):
    DEFAULT = object()

    def __init__(self, default: Union[Values] = DEFAULT):
        self.__value = default

    def __set_name__(self, _, name):
        self.private_name = name

    def __set__(self, _, value):
        self.__value = self.cast(value)

    def __get__(self, instance, _=None) -> Values:
        if self.__value is self.DEFAULT:
            raise KeyError
        return self.__value

    @abstractmethod
    def cast(self, string_value: str) -> Values:
        pass


class IntParam(TypedParameter):
    def cast(self, string_value: str) -> Values:
        return int(string_value)


class FloatParam(TypedParameter):
    def cast(self, string_value: str) -> Values:
        return float(string_value)


class StrParam(TypedParameter):
    def cast(self, string_value: str) -> Values:
        return string_value


class MetaConfig(type):
    def __new__(mcs, name, parents, attributes):
        MetaConfig.extend_annotations(attributes)
        cls = super().__new__(mcs, name, parents, attributes)
        return cls

    @staticmethod
    def extend_annotations(attributes):
        annotations = attributes.get("__annotations__", {})
        for attr, value in attributes.items():
            if MetaConfig.is_user_attribute(attr):
                if attr not in annotations:
                    annotations[attr] = str
        attributes["__annotations__"] = annotations

    @staticmethod
    def is_user_attribute(attr):
        return not (attr.startswith("__") or attr.endswith("__"))


class BaseConfig(metaclass=MetaConfig):
    def __init__(self, storage: ConfigStorage):
        self.__storage = storage
        for name, type_ in get_type_hints(self.__class__).items():
            if name != "_BaseConfig__get_raw_value":
                raw_value = self.__get_raw_value(name)
                setattr(self, name, type_(raw_value))

    def __get_raw_value(self, name: str) -> Values:
        try:
            return self.__storage[name]
        except KeyError:
            if hasattr(self, name):
                return getattr(self, name)
        raise KeyError(name)
