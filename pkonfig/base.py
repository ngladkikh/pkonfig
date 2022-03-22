from abc import ABC, ABCMeta, abstractmethod
from inspect import isclass, isdatadescriptor, ismethod
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
    nullable: bool

    def __init__(
        self,
        default=NOT_SET,
        no_cache=False,
        alias: Optional[str] = None,
        nullable=False,
    ):
        self.no_cache = no_cache
        self.default: Union[T, object] = default
        self.value: Union[T, object] = NOT_SET
        self.alias = alias
        self.nullable = default is None or nullable

    def __set_name__(self, _, name):
        self.name = self.alias if self.alias is not None else name

    def __set__(self, _, value):
        value = self.cast(value)
        self.validate(value)
        self.value = value

    def __get__(self, instance: "BaseConfig", _=None) -> Union[T, object]:
        if self.should_get_from_storage():
            value = self.get_from_storage(instance)
            if value is not None:
                value = self.cast(value)
                self.validate(value)
            self.value = value
        return self.value

    def get_from_storage(self, instance: "BaseConfig") -> Any:
        storage = instance.get_storage()
        value = storage.get(self.name, self.default)
        if value is None and not self.nullable:
            raise ValueError(f"{self.name} is not nullable")
        elif value is NOT_SET:
            raise KeyError(self.name)
        return value

    def should_get_from_storage(self) -> bool:
        return self.value is NOT_SET or self.no_cache

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def validate(self, value: Any) -> None:
        pass


TypeMapping = Dict[Type, Type[Field]]


class TypeMapper(ABC):
    type_mapping: TypeMapping = {}

    def __init__(self, mappings: Optional[TypeMapping] = None):
        if mappings:
            self.type_mapping.update(mappings)

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
        return not (isdatadescriptor(attribute) or isclass(attribute))

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
            mapper = getattr(cls, "_mapper", None)
            if mapper and isinstance(mapper, TypeMapper):
                return mapper
        return None


class BaseConfig(metaclass=MetaConfig):
    _mapper: TypeMapper
    _storage: Mapping
    _alias: Optional[str] = None

    def get_storage(self) -> Mapping:
        return self._storage

    def set_storage(self, storage: Mapping) -> None:
        self._storage = storage

    def is_user_attr(self, name: str) -> bool:
        if name.startswith("_"):
            return False

        if hasattr(self, name):
            attribute = getattr(self, name)
            return not (ismethod(attribute) or isclass(attribute))

        return True

    def user_fields(self):
        return filter(self.is_user_attr, get_type_hints(self).keys())

    def check_all_fields(self):
        for name in self.user_fields():
            attr = getattr(self, name)
            if isinstance(attr, BaseConfig):
                alias = attr._alias if attr._alias else name
                attr.set_storage(self.get_storage().get(alias, {}))
                attr.check_all_fields()


class BaseOuterConfig(BaseConfig):
    def __init__(self, storage: Mapping):
        self.set_storage(storage)
        self.check_all_fields()
