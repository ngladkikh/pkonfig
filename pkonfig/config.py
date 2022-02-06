from pathlib import Path
from typing import Any, Dict, Mapping, Type, Union, get_type_hints

Values = Union[str, int, float, Path]
ConfigStorage = Mapping[str, Any]


class MetaConfig(type):
    def __new__(mcs, name, parents, attributes):
        annotations = attributes.get("__annotations__", {})
        attributes_with_defaults = {
            k: annotations.get(k, type(v))
            for k, v in attributes.items()
            if MetaConfig.is_user_attr(k, v)
        }
        attributes["_attributes_with_defaults"] = attributes_with_defaults
        cls = super().__new__(mcs, name, parents, attributes)
        return cls

    @staticmethod
    def is_user_attr(name: str, attr: Any) -> bool:
        if not name.startswith("__"):
            return not callable(attr)
        return False


class BaseConfig(metaclass=MetaConfig):
    _attributes_with_defaults: Dict[str, Type]

    def __init__(self, storage: ConfigStorage):
        self.__storage = storage
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
            return self.__storage[name]
        except KeyError:
            if hasattr(self, name):
                return getattr(self, name)
        raise KeyError(name)
