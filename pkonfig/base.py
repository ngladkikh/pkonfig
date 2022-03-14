from abc import ABC, ABCMeta, abstractmethod
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
    Union,
    get_type_hints,
)


T = TypeVar("T")
NOT_SET = object()


class Field(ABC, Generic[T]):
    default: Union[T, object]
    value: Union[T, object]

    def __init__(self, default=NOT_SET, no_cache=False, alias: Optional[str] = None):
        self.no_cache = no_cache
        self.default: Union[T, object] = default
        self.value: Union[T, object] = NOT_SET
        self.alias = alias

    def __set_name__(self, _, name):
        self.name = self.alias if self.alias is not None else name

    def __set__(self, _, value):
        value = self.cast(value)
        self.validate(value)
        self.value = value

    def __get__(self, instance: "BaseConfig", _=None) -> Union[T, object]:
        if self.should_get_from_storage():
            value = self.get_from_storage(instance)
            value = self.cast(value)
            self.validate(value)
            self.value = value
        return self.value

    def get_from_storage(self, instance: "BaseConfig") -> Any:
        value = self.default
        try:
            storage = instance.get_storage()
            if storage is not None:
                value = storage[self.name]
        except KeyError:
            if self.default is NOT_SET:
                raise KeyError(self.name)
        return value

    def should_get_from_storage(self) -> bool:
        return self.value is NOT_SET or self.no_cache

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def validate(self, value: Any) -> None:
        pass


class TypeMapper(ABC):
    def replace_fields_with_descriptors(
        self, attributes: Dict[str, Any], type_hints: Dict[str, Type]
    ) -> None:
        for name in filter(lambda x: not x.startswith("_"), type_hints.keys()):
            attribute = attributes.get(name, NOT_SET)
            if self.replace(attribute):
                hint = type_hints[name]
                descriptor = self.descriptor(hint, attribute)
                attributes[name] = descriptor

    @staticmethod
    def replace(attribute):
        return not (
            isfunction(attribute)
            or isdatadescriptor(attribute)
            or ismethoddescriptor(attribute)
            or isclass(attribute)
        )

    @abstractmethod
    def descriptor(self, type_: Type, value: Any = NOT_SET) -> Field:
        pass


class MetaConfig(ABCMeta):
    def __new__(mcs, name, parents, attributes):
        MetaConfig.extend_annotations(attributes)
        mapper = MetaConfig.get_mapper(attributes, parents)
        if mapper:
            mapper.replace_fields_with_descriptors(
                attributes, attributes.get("__annotations__", {})
            )
        cls = super().__new__(mcs, name, parents, attributes)
        return cls

    @staticmethod
    def extend_annotations(attributes: Dict[str, Any]) -> None:
        annotations = attributes.get("__annotations__", {})
        for name, attr in attributes.items():
            if not name.startswith("_") or isclass(attr):
                if name not in annotations:
                    attr_type = type(attr)
                    if issubclass(attr_type, Field):
                        annotation = get_type_hints(attr.cast).get("return", Any)
                    else:
                        annotation = attr_type
                    annotations[name] = annotation
        attributes["__annotations__"] = annotations

    @staticmethod
    def get_mapper(
        attributes: Dict[str, Any], parents: Iterable[Type]
    ) -> Optional[TypeMapper]:
        for name, attribute in attributes.items():
            if isinstance(attribute, TypeMapper):
                return attribute
        for cls in parents:
            mapper = getattr(cls, "Mapper", None)
            if mapper and isinstance(mapper, TypeMapper):
                return mapper
        return None


class BaseConfig(metaclass=MetaConfig):
    _storage: Optional[Mapping]
    Mapper: TypeMapper

    def __init__(self, fail_fast: bool = True):
        self._storage = None
        self._fail_fast = fail_fast
        self._validation_done: bool = False

    def get_storage(self) -> Optional[Mapping]:
        return self._storage

    def is_user_attr(self, name: str) -> bool:
        if name.startswith("_"):
            return False

        if hasattr(self, name):
            attribute = getattr(self, name)
            return not (
                ismethod(attribute) or isfunction(attribute) or isclass(attribute)
            )

        return True

    def user_fields(self):
        return filter(self.is_user_attr, get_type_hints(self).keys())

    def check_all_fields(self):
        for name in self.user_fields():
            getattr(self, name)
        self._validation_done = True


class BaseOuterConfig(BaseConfig, ABC):
    def __init__(self, storage: Mapping, fail_fast=True):
        super().__init__(fail_fast=fail_fast)
        self._storage = storage
        if self._fail_fast:
            self.check_all_fields()


TInner = TypeVar("TInner", bound="BaseInnerConfig")


class BaseInnerConfig(BaseConfig, ABC):
    def __init__(self, fail_fast: bool = True, alias: Optional[str] = None):
        self._alias = alias
        super().__init__(fail_fast)

    def __set_name__(self, _, name):
        self._name = self._alias if self._alias is not None else name

    def __get__(self, instance: BaseConfig, _=None) -> "BaseInnerConfig":
        if self._storage is None:
            parent_storage = instance.get_storage()
            if parent_storage:
                self._storage = parent_storage[self._name]
        if not (self._validation_done and self._fail_fast):
            self.check_all_fields()
        return self
