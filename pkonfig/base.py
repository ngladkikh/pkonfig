from abc import ABC, ABCMeta, abstractmethod
from collections import ChainMap
from collections.abc import Mapping
from inspect import isclass, isdatadescriptor
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Reversible,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from pkonfig.errors import ConfigTypeError, ConfigValueNotFoundError
from pkonfig.storage.base import BaseStorage, DictStorage, InternalKey

NOT_SET = "NOT_SET"
T = TypeVar("T")


class Field(Generic[T]):
    """Base config attribute descriptor"""

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable: bool = False,
    ):
        self.default: Union[T, object] = default
        self.alias: str = alias
        self.nullable = default is None or nullable
        self._cache: T = NOT_SET    # type:ignore
        self._path: InternalKey = tuple()

    @property
    def error_name(self) -> str:
        return ".".join(self._path)

    def __set_name__(self, _: Type["BaseConfig"], name: str) -> None:
        self.alias = self.alias or name

    def __set__(self, instance: "BaseConfig", value) -> None:
        value = self._cast(value)
        self._validate(value)
        self._cache = value

    def __get__(self, instance: "BaseConfig", _=None) -> T:
        if self._cache is NOT_SET:
            self._cache = self.get_from_storage(instance)
        return self._cache

    def get_from_storage(self, instance: "BaseConfig") -> T:
        value = self._get_from_storage(instance)
        if value is None and not self.nullable:
            raise ConfigTypeError(f"Field {self.error_name} is not nullable")
        if value is not None:
            value = self._cast(value)
            self._validate(value)
        return value

    def _get_from_storage(self, instance: "BaseConfig") -> Any:
        storage = instance.get_storage()
        self._path = (*instance.get_roo_path(), self.alias)
        if self._path in storage:
            return storage[self._path]
        if self.default is NOT_SET:
            raise ConfigValueNotFoundError(self.error_name)
        return self.default

    def _cast(self, value: Any) -> T:
        try:
            return self.cast(value)
        except (ValueError, TypeError) as exc:
            raise ConfigTypeError(f"{self.error_name} failed to cast {value}") from exc

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def _validate(self, value: Any) -> None:
        try:
            return self.validate(value)
        except TypeError as exc:
            raise ConfigTypeError(f"{self.error_name}: {value} invalid") from exc

    def validate(self, value: Any) -> None:
        pass


TypeMapping = Dict[Type, Type["Field"]]
C = TypeVar("C", bound="BaseConfig")


class TypeMapper(ABC):
    """Replaces user defined attributes with typed descriptors"""

    type_mapping: TypeMapping = {}

    def __init__(self, mappings: Optional[TypeMapping] = None):
        if mappings:
            self.type_mapping.update(mappings)

    def replace_fields_with_descriptors(
        self, attributes: Dict[str, Any], type_hints: Dict[str, Type]
    ) -> None:
        inner_configs = []
        attribute_names = []
        for name in filter(self.public_attribute, type_hints.keys()):
            attribute = attributes.get(name, NOT_SET)
            if self.replace(attribute):
                hint = type_hints[name]
                descriptor = self.descriptor(hint, attribute)
                attributes[name] = descriptor
                if isinstance(attribute, BaseConfig):
                    inner_configs.append(attribute)
                else:
                    attribute_names.append(name)
        attributes["_inner_configs"] = inner_configs
        attributes["_field_names"] = attribute_names

    @staticmethod
    def public_attribute(attr_name: str) -> bool:
        return not attr_name.startswith("_")

    @staticmethod
    def replace(attribute: Any):
        return not (isdatadescriptor(attribute) or isclass(attribute))

    @abstractmethod
    def descriptor(self, type_: T, value: Any = NOT_SET) -> Field[T]:
        pass


class MetaConfig(ABCMeta):
    """Replaces class-level attributes with Field descriptors"""

    def __new__(mcs, name, parents, attributes):  # pylint: disable=arguments-differ
        MetaConfig.extend_annotations(attributes)
        mapper = MetaConfig.get_mapper(attributes, parents)
        if mapper:
            mapper.replace_fields_with_descriptors(
                attributes, attributes.get("__annotations__", {})
            )

        cls = super().__new__(mcs, name, parents, attributes)
        if not getattr(cls, "__get__", None):
            cls.__set_name__ = MetaConfig.__set_name
            cls.__get__ = MetaConfig.__get

        return cls

    @staticmethod
    def extend_annotations(attributes: Dict[str, Any]) -> None:
        """Extends class annotations using default values types or fields cast method annotation"""

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
        attributes: Dict[str, Any], parents: Reversible[Type]
    ) -> Optional[TypeMapper]:
        """Get mapper from class attribute or take it from parent"""

        mapper = attributes.get("_mapper")
        if mapper and isinstance(mapper, TypeMapper):
            return mapper

        for cls in reversed(parents):
            mapper = getattr(cls, "_mapper", None)
            if mapper and isinstance(mapper, TypeMapper):
                return mapper
        return None

    @staticmethod
    def __set_name(config: C, _, name: str) -> None:
        config.set_alias(name)

    @staticmethod
    def __get(config: C, parent: C, _=None) -> C:
        if not config.get_storage():
            config.set_root_path((*parent.get_roo_path(), config.get_alias()))
            config.set_storage(parent.get_storage())
        return config


class BaseConfig(metaclass=MetaConfig):
    _inner_configs: List["BaseConfig"]
    _field_names: List[str]
    _storage: ChainMap
    _inner: bool = False

    def __init__(
        self,
        *storages: Union[dict, BaseStorage],
        alias: str = "",
        fail_fast: bool = True,
    ) -> None:
        internal_storages = []
        for s in storages:
            if isinstance(s, BaseStorage):
                internal_storages.append(s)
            elif isinstance(s, Mapping):
                internal_storages.append(DictStorage(**s))
            else:
                raise TypeError(f"Unsupported storage type: {type(s)}")
        self._storage = ChainMap(*internal_storages)    # type:ignore
        self._alias = alias
        self._root_path: InternalKey = (alias,) if alias else tuple()
        if fail_fast:
            self.check()

    def get_roo_path(self) -> InternalKey:
        return self._root_path

    def set_root_path(self, path: InternalKey) -> None:
        self._root_path = path

    def get_storage(self) -> ChainMap:
        return self._storage

    def set_storage(self, storage: ChainMap) -> None:
        self._storage = storage

    def set_alias(self, alias: str) -> None:
        self._alias = self._alias or alias

    def get_alias(self) -> str:
        return self._alias

    def check(self) -> None:
        if self._storage:
            for name in self._field_names:
                getattr(self, name)
            for config in self._inner_configs:
                config.check()
