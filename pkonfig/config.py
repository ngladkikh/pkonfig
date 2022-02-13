from pathlib import Path
from typing import Any, Dict, Mapping, Type, TypeVar, Union, get_type_hints

from pkonfig.base import BaseConfig

Values = Union[str, int, float, Path]
ConfigStorage = Mapping[str, Any]
Config = Union["OuterMostConfig", "EmbeddedConfig"]
TEmbedded = TypeVar("TEmbedded", bound="EmbeddedConfig")
Annotations = Dict[str, Type]


class OuterMostConfig(BaseConfig):
    _attributes_with_defaults: Dict[str, Type]
    _name: str

    def __init__(self, storage: Mapping):
        self._storage = storage
        self._hints = get_type_hints(self)
        for name, type_ in self._attributes_with_defaults.items():
            self._set_validates_attribute(name, type_)

        for name, type_ in ((k, v) for k, v in self._hints.items() if self._is_user_field(k)):
            self._set_validates_attribute(name, type_)

    def _set_validates_attribute(self, name, type_):
        raw_value = self.__get_raw_value(name)
        value = type_(raw_value)
        if name in self._hints:
            value_type = type(value)
            value_hint = self._hints[name]
            if value_type is not value_hint:
                raise AttributeError(f"{value} for {name} is {value_type} not {value_hint}")
        setattr(self, name, value)

    @staticmethod
    def _is_user_field(attr_name: str) -> bool:
        return not attr_name.startswith("_")

    def __get_raw_value(self, name: str) -> Values:
        try:
            return self._storage[name]
        except KeyError:
            if hasattr(self, name):
                return getattr(self, name)
        raise KeyError(name)


class EmbeddedConfig(BaseConfig):

    def __init__(self):
        self._storage = None
        self._name = None

    def __set_name__(self, _, name):
        self._name = name

    def __get__(self, instance: Config, _=None) -> TEmbedded:
        if self._storage is None:
            self._storage = instance.get_storage()[self._name]
        return self
