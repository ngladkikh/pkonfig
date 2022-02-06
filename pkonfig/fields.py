from abc import ABC, abstractmethod
from typing import Union

from pkonfig.config import Values


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
