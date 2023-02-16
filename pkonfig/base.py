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
DEFAULT_PREFIX = "APP"
DEFAULT_DELIMITER = "__"
TypeMapping = Dict[Type, Type["Attribute"]]


class TypeMapper(ABC):
    """Replaces user defined attributes with typed descriptors"""

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
    def descriptor(self, type_: Type, value: Any = NOT_SET) -> "Field":
        pass


class Field(Generic[T]):
    """Base config attribute descriptor"""

    def __init__(
        self,
        default=NOT_SET,
        alias: Optional[str] = None,
        nullable=False,
    ):
        self.default: Union[T, object] = default
        self.value: Union[T, object] = NOT_SET
        self.alias = alias
        self.nullable = default is None or nullable
        self.path: Optional[str] = None

    def __set_name__(self, obj: "BaseConfig", name: str) -> None:
        self.alias = self.alias if self.alias is not None else name.upper()

    def __set__(self, _, value) -> None:
        value = self.cast(value)
        self.validate(value)
        self.value = value

    def __get__(self, instance: "BaseConfig", _=None) -> Union[T, object]:
        if self.value is NOT_SET:
            value = self.get_from_storage(instance)
            if value is not None:
                value = self.cast(value)
                self.validate(value)
            else:
                if not self.nullable:
                    raise TypeError(f"{self.path} value is None")
            self.value = value
        return self.value

    def get_from_storage(self, instance: "BaseConfig") -> Any:
        storage = instance.get_storage()
        if storage is None:
            raise AttributeError("no storage")
        self.path = instance.get_roo_path() + self.alias
        try:
            return storage[self.path]
        except KeyError:
            if self.default is not NOT_SET:
                return self.default
            raise

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def validate(self, value: Any) -> None:
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


class Storage:
    """Plain config data storage"""
    def __init__(
        self,
        multilevel_mapping: Optional[Mapping] = None,
        delimiter: str = DEFAULT_DELIMITER,
        prefix: str = DEFAULT_PREFIX,
    ) -> None:
        self.delimiter = delimiter
        self.prefix = prefix
        if multilevel_mapping:
            parent = self.prefix + self.delimiter if self.prefix else ""
            self._data = self.flatten(multilevel_mapping, parent)
        else:
            self._data = {}

    def __getitem__(self, key: str) -> Any:
        return self._data[key.upper()]

    def get(self, key: str, default: Any) -> Any:
        return self._data.get(key.upper(), default)

    def empty(self) -> bool:
        return not bool(self._data)

    def flatten(
        self,
        multilevel_mapping: Mapping,
        parent: str = "",
    ) -> Mapping:
        res = {}
        for key, value in multilevel_mapping.items():
            key = parent + key.upper()
            if isinstance(value, Mapping):
                res.update(self.flatten(value, key + self.delimiter))
            else:
                res[key] = value
        return res


class BaseConfig(Generic[T], metaclass=MetaConfig):

    def __init__(
        self,
        storage: Union[None, dict, Storage] = None,
        alias: Optional[str] = DEFAULT_PREFIX,
        delimiter: str = DEFAULT_DELIMITER,
    ) -> None:
        self._storage: Storage = storage if isinstance(storage, Storage) else Storage(storage, delimiter, alias)
        self._alias = alias
        self._delimiter = delimiter
        self._root_path: str = alias + delimiter if alias else ""

    def get_delimiter(self) -> str:
        return self._delimiter

    def get_roo_path(self) -> str:
        return self._root_path

    def get_storage(self) -> Storage:
        return self._storage

    def __set_name__(self, cls: Type["BaseConfig"], name: str) -> None:
        self._alias = self._alias if self._alias is not DEFAULT_PREFIX else name.upper()

    def __get__(self: T, instance: "BaseConfig", _=None) -> T:
        if self._storage.empty():
            self._delimiter = instance.get_delimiter()
            self._root_path = instance.get_roo_path() + self._alias + self._delimiter
            self._storage = instance.get_storage()
        return self

    def is_user_attr(self, name: str) -> bool:
        if name.startswith("_"):
            return False

        if hasattr(self, name):
            attribute = getattr(self, name)
            return not (ismethod(attribute) or isclass(attribute))

        return True
