from abc import ABC, abstractmethod
from inspect import isfunction, ismethod
from typing import Any, Dict, Mapping, Optional

from pkonfig.config import Annotations


def is_user_attr(name: str, attribute: Any) -> bool:
    if not name.startswith("_"):
        return not (ismethod(attribute) or isfunction(attribute))
    return False


class TypedParameter(ABC):
    DEFAULT = object()

    def __init__(self, default=DEFAULT):
        self.__value = default

    def __set_name__(self, _, name):
        self.private_name = name

    def __set__(self, _, value):
        self.__value = self.cast(value)

    def __get__(self, instance, _=None):
        if self.__value is self.DEFAULT:
            raise KeyError
        return self.__value

    @abstractmethod
    def cast(self, string_value: str):
        pass


def get_descriptor(attr: Any, annotations: Annotations) -> TypedParameter:
    pass


def should_be_replaced(name: str, attr: Any) -> bool:
    pass


def extend_annotations(attributes: Dict[str, Any]) -> None:
    pass
    # for name, attr in attributes.items():
    #     if should_be_replaced(name, attr):
    #         attributes[name] = get_descriptor(attr, annotations)


def replace_user_attributes_with_descriptors(attributes: Dict[str, Any]):
    pass
    # for name, type_ in annotations.items():
    #     if name not in attributes:


class MetaConfig(type):
    def __new__(mcs, name, parents, attributes):
        extend_annotations(attributes)
        replace_user_attributes_with_descriptors(attributes)
        cls = super().__new__(mcs, name, parents, attributes)
        return cls


class BaseConfig(metaclass=MetaConfig):
    _storage: Optional[Mapping]

    def get_storage(self) -> Mapping:
        return self._storage
