from abc import ABC, ABCMeta, abstractmethod
from functools import partial
from inspect import isfunction, ismethod
from typing import Any, Dict, Mapping, Optional, Tuple, Type, TypeVar, get_type_hints


TEmbedded = TypeVar("TEmbedded", bound="EmbeddedConfig")
RETURN_TYPE = TypeVar("RETURN_TYPE")
NOT_SET = object()


class ConfigFromStorageBase:
    _storage: Optional[Mapping]

    def get_storage(self) -> Mapping:
        return self._storage


class TypedParameter(ABC):
    _return_type: RETURN_TYPE

    @property
    @abstractmethod
    def returns(self):
        return self._return_type

    def __init__(self, default=NOT_SET, no_cache=True):
        self.no_cache = no_cache
        self.default = default
        self.value = default

    def __set_name__(self, _, name):
        self.name = name

    def __set__(self, _, value):
        self.value = self.cast(value)

    def __get__(self, instance: ConfigFromStorageBase, _=None) -> RETURN_TYPE:
        if self.should_get_from_storage():
            value = self.get_from_storage(instance)
            self.value = self.cast(value)
            self.validate()
        return self.value

    def get_from_storage(self, instance: ConfigFromStorageBase) -> Any:
        try:
            value = instance.get_storage()[self.name]
        except KeyError:
            if self.default is NOT_SET:
                raise KeyError(self.name)
            value = self.default
        return value

    def should_get_from_storage(self) -> bool:
        return self.value is NOT_SET or self.no_cache

    @abstractmethod
    def cast(self, string_value: str) -> RETURN_TYPE:
        pass

    def validate(self):
        pass


class TypeMapper(ABC):
    @abstractmethod
    def descriptor(
        self, type_: Type, value: Any = NOT_SET
    ) -> TypedParameter:
        pass


def extend_annotations(attributes: Dict[str, Any]) -> None:
    annotations = attributes.get("__annotations__", {})
    for name, attr in attributes.items():
        if not name.startswith("_"):
            if name not in annotations:
                attr_type = type(attr)
                annotation = attr.returns if issubclass(attr_type, TypedParameter) else attr_type
                annotations[name] = annotation
    attributes["__annotations__"] = annotations


def is_user_attr(name: str, object_: Any) -> bool:
    if name.startswith("_"):
        return False

    if hasattr(object_, name):
        attribute = getattr(object_, name)
        return not (ismethod(attribute) or isfunction(attribute))

    return True


class IntParam(TypedParameter):
    returns = int

    def cast(self, string_value: str):
        return int(string_value)


class FloatParam(TypedParameter):
    returns = float

    def cast(self, string_value: str):
        return float(string_value)


class StrParam(TypedParameter):
    returns = str

    def cast(self, string_value: str):
        return string_value


TYPE_MAP: Dict[Type, Type[TypedParameter]] = {
    int: IntParam,
    float: FloatParam,
    str: StrParam
}


# def get_descriptor(annotation: Type, value: Any) -> TypedParameter:
#     descriptor_class = TYPE_MAP.get(annotation, StrParam)
#     return descriptor_class(value)


def replace_fields_with_descriptors(attributes: Dict[str, Any], parents):
    mapper = None
    try:
        mapper = attributes["_mapper"]
    except KeyError:
        for p in parents:
            try:
                mapper = p._mapper
                break
            except AttributeError:
                pass
    if mapper is None:
        return

    def get_descriptor(annotation: Type, value: Any) -> TypedParameter:
        descriptor_class = mapper.get(annotation, StrParam)
        return descriptor_class(value)

    type_hints = attributes["__annotations__"]
    for name in type_hints.keys():
        if name.startswith("_"):
            continue

        attribute = attributes.get(name, NOT_SET)
        if parents and issubclass(type(attribute), parents[0]):
            continue
        if isfunction(attribute):
            continue
        if issubclass(type(attribute), TypedParameter):
            continue
        hint = type_hints[name]
        descriptor = get_descriptor(hint, attribute)
        attributes[name] = descriptor


class MetaConfig(ABCMeta):
    def __new__(mcs, name, parents, attributes):
        extend_annotations(attributes)
        replace_fields_with_descriptors(attributes, parents)
        cls = super().__new__(mcs, name, parents, attributes)
        return cls


class AbstractBaseConfig(ConfigFromStorageBase, metaclass=MetaConfig):

    def __init__(
        self,
        storage: Optional[Mapping] = None,
        fail_fast: bool = True
    ):
        self._fail_fast = fail_fast
        self._storage = storage
        self._validation_done: bool = False
        if self._fail_fast and self._storage is not None:
            self.check_all_fields()

    def __set_name__(self, _, name):
        self._name = name

    def __get__(
        self, instance: ConfigFromStorageBase, _=None
    ) -> TEmbedded:
        if self._storage is None:
            self._storage = instance.get_storage()[self._name]
        if not (self._validation_done and self._fail_fast):
            self.check_all_fields()
        return self

    def user_fields_filter(self):
        return partial(is_user_attr, object_=self)

    def user_fields(self):
        return filter(
            self.user_fields_filter(),
            get_type_hints(self).keys()
        )

    def check_all_fields(self):
        for name in self.user_fields():
            getattr(self, name)
