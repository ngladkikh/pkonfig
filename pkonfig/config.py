from pathlib import Path
from typing import Any, Mapping, Union, get_type_hints

Values = Union[str, int, float, Path]
ConfigStorage = Mapping[str, Any]


class MetaConfig(type):
    def __new__(mcs, name, parents, attributes):
        MetaConfig.extend_annotations(attributes)
        cls = super().__new__(mcs, name, parents, attributes)
        return cls

    @staticmethod
    def extend_annotations(attributes):
        annotations = attributes.get("__annotations__", {})
        for attr, value in attributes.items():
            if MetaConfig.is_user_field(attr):
                if attr not in annotations:
                    annotations[attr] = str
        attributes["__annotations__"] = annotations

    @staticmethod
    def is_user_field(attr) -> bool:
        return not (callable(attr) or (attr.startswith("__") or attr.endswith("__")))


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
