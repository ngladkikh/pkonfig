from abc import ABC, ABCMeta, abstractmethod
from functools import partial
from inspect import isclass, isdatadescriptor, isfunction, ismethod, ismethoddescriptor
from typing import (
    Any,
    Dict,
    Generic,
    Iterable,
    Mapping,
    Optional,
    Type,
    TypeVar,
    get_type_hints,
)


TEmbedded = TypeVar("TEmbedded", bound="EmbeddedConfig")
T = TypeVar("T")
RETURN_TYPE = TypeVar("RETURN_TYPE")
NOT_SET = object()


class ConfigFromStorageBase:
    _storage: Optional[Mapping]
    Mapper: "TypeMapper"

    def get_storage(self) -> Optional[Mapping]:
        return self._storage


class TypedParameter(ABC, Generic[T]):
    def __init__(self, default=NOT_SET, no_cache=False, alias: Optional[str] = None):
        self.no_cache = no_cache
        self.default = default
        self.value = NOT_SET
        self.alias = alias

    def __set_name__(self, _, name):
        self.name = self.alias if self.alias is not None else name

    def __set__(self, _, value):
        value = self.cast(value)
        self.validate(value)
        self.value = value

    def __get__(self, instance: ConfigFromStorageBase, _=None) -> T:
        if self.should_get_from_storage():
            value = self.get_from_storage(instance)
            value = self.cast(value)
            self.validate(value)
            self.value = value
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
    def cast(self, value: Any) -> T:
        pass

    @staticmethod
    def validate(value: Any) -> None:
        pass


class TypeMapper(ABC):
    @abstractmethod
    def descriptor(self, type_: Type, value: Any = NOT_SET) -> TypedParameter:
        pass


def get_mapper(
    attributes: Dict[str, Any], parents: Iterable[Type]
) -> Optional[TypeMapper]:
    for name, attribute in attributes.items():
        if isclass(attribute) and issubclass(attribute, TypeMapper):
            return attribute()
    for cls in parents:
        mapper = getattr(cls, "Mapper", None)
        if mapper and isclass(mapper) and issubclass(mapper, TypeMapper):
            return mapper()


def extend_annotations(attributes: Dict[str, Any]) -> None:
    annotations = attributes.get("__annotations__", {})
    for name, attr in attributes.items():
        if not name.startswith("_") or isclass(attr):
            if name not in annotations:
                attr_type = type(attr)
                if issubclass(attr_type, TypedParameter):
                    annotation = get_type_hints(attr.cast).get("return", Any)
                else:
                    annotation = attr_type
                annotations[name] = annotation
    attributes["__annotations__"] = annotations


def is_user_attr(name: str, object_: Any) -> bool:
    if name.startswith("_"):
        return False

    if hasattr(object_, name):
        attribute = getattr(object_, name)
        return not (ismethod(attribute) or isfunction(attribute) or isclass(attribute))

    return True


def replace(attribute):
    return not (
        isfunction(attribute)
        or isdatadescriptor(attribute)
        or ismethoddescriptor(attribute)
        or isclass(attribute)
    )


def replace_fields_with_descriptors(
    attributes: Dict[str, Any], mapper: TypeMapper
) -> None:
    type_hints = attributes["__annotations__"]
    for name in filter(lambda x: not x.startswith("_"), type_hints.keys()):
        attribute = attributes.get(name, NOT_SET)
        if replace(attribute):
            hint = type_hints[name]
            descriptor = mapper.descriptor(hint, attribute)
            attributes[name] = descriptor


class MetaConfig(ABCMeta):
    def __new__(mcs, name, parents, attributes):
        extend_annotations(attributes)
        mapper = get_mapper(attributes, parents)
        if mapper:
            replace_fields_with_descriptors(attributes, mapper)
        cls = super().__new__(mcs, name, parents, attributes)
        return cls


class AbstractBaseConfig(ConfigFromStorageBase, metaclass=MetaConfig):
    def __init__(self, fail_fast: bool = True):
        self._storage = None
        self._fail_fast = fail_fast
        self._validation_done: bool = False

    def user_fields_filter(self):
        return partial(is_user_attr, object_=self)

    def user_fields(self):
        return filter(self.user_fields_filter(), get_type_hints(self).keys())

    def check_all_fields(self):
        for name in self.user_fields():
            getattr(self, name)
        self._validation_done = True


class BaseOuterConfig(AbstractBaseConfig, ABC):
    def __init__(self, storage: Mapping, fail_fast=True):
        super().__init__(fail_fast=fail_fast)
        self._storage = storage
        if self._fail_fast:
            self.check_all_fields()


class BaseInnerConfig(AbstractBaseConfig, ABC):
    def __set_name__(self, _, name):
        self._name = name

    def __get__(self, instance: ConfigFromStorageBase, _=None) -> TEmbedded:
        if self._storage is None:
            self._storage = instance.get_storage()[self._name]
        if not (self._validation_done and self._fail_fast):
            self.check_all_fields()
        return self
