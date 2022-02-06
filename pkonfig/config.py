from abc import ABC, abstractmethod
from typing import Any, Mapping, Union, get_type_hints

Values = Union[str, int, float]
ConfigStorage = Mapping[str, Any]


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
