from abc import ABC, ABCMeta, abstractmethod
from collections import ChainMap
from inspect import isclass, isdatadescriptor
from typing import (
    Any,
    Dict,
    Generic,
    Iterator,
    Mapping,
    MutableMapping,
    Optional,
    Reversible,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

InternalKey = Tuple[str, ...]
InternalStorage = Union[Dict[InternalKey, Any], ChainMap[InternalKey, Any]]
NOT_SET = object()
T = TypeVar("T")


class Field(Generic[T]):
    """Base config attribute descriptor"""

    def __init__(
        self,
        default=NOT_SET,
        alias: str = "",
        nullable=False,
        no_cache: bool = False,
    ):
        self.default: Union[T, object] = default
        self.alias = alias
        self.nullable = default is None or nullable
        self.no_cache = no_cache
        self.path: Optional[InternalKey] = None
        self._cache: InternalStorage = {}

    def __set_name__(self, _, name: str) -> None:
        self.alias = self.alias or name

    def __set__(self, instance: "BaseConfig", value) -> None:
        value = self.cast(value)
        self.validate(value)
        path = self.get_path(instance)
        self._cache[path] = value

    def __get__(self, instance: "BaseConfig", _=None) -> Union[T, object]:
        path = self.get_path(instance)
        value = NOT_SET if self.no_cache else self._cache.get(path, NOT_SET)
        if value is NOT_SET:
            value = self.get_from_storage(instance)
            if value is not None:
                value = self.cast(value)
                self.validate(value)
            else:
                if not self.nullable:
                    raise TypeError(f"{self.path} value is None")
            self._cache[path] = value
        return value

    def get_path(self, instance: "BaseConfig") -> InternalKey:
        return *instance.get_roo_path(), self.alias

    def get_from_storage(self, instance: "BaseConfig") -> Any:
        storage = instance.get_storage()
        path = self.get_path(instance)
        try:
            return storage[path]
        except KeyError as exc:
            if self.default is not NOT_SET:
                return self.default
            raise KeyError({".".join(path)}) from exc

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def validate(self, value: Any) -> None:
        pass


TypeMapping = Dict[Type, Type["Field"]]


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
    def descriptor(self, type_: T, value: Any = NOT_SET) -> Field[T]:
        pass


def set_name(config: "BaseConfig", _, name: str) -> None:
    config.set_alias(name)


C = TypeVar("C", bound="BaseConfig")


def get(config: C, parent: "BaseConfig", _=None) -> C:
    # pylint: disable=protected-access
    if not config.get_storage():
        config._root_path = (*parent.get_roo_path(), config.get_alias())
        config._storage = parent.get_storage()
    return config


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
            cls.__set_name__ = set_name
            cls.__get__ = get

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


class BaseStorage(MutableMapping, ABC):
    """Plain config data storage"""

    @abstractmethod
    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        ...

    def __delitem__(self, key: Tuple[str, ...]) -> Any:
        raise NotImplementedError

    def __setitem__(self, key: str, value: Any) -> None:
        raise NotImplementedError

    def __iter__(self) -> Iterator[Any]:
        raise NotImplementedError


class Storage(BaseStorage):
    def __init__(
        self,
        *multilevel_mappings: Mapping,
    ) -> None:
        self._multilevel_mappings = multilevel_mappings

    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        for mapping in self._multilevel_mappings:
            for partial_key in key[:-1]:
                if partial_key in mapping:
                    mapping = mapping[partial_key]
            if key[-1] in mapping:
                return mapping[key[-1]]
        raise KeyError(key)

    def __len__(self) -> int:
        return len(self._multilevel_mappings)


class BaseConfig(metaclass=MetaConfig):
    def __init__(
        self,
        *storages: Union[dict, BaseStorage],
        alias: str = "",
    ) -> None:
        internal_storages = []
        for s in storages:
            if isinstance(s, BaseStorage):
                internal_storages.append(s)
            else:
                internal_storages.append(Storage(s))
        self._storage: InternalStorage = ChainMap(*internal_storages)
        self._alias = alias
        self._root_path: InternalKey = (alias,) if alias else tuple()

    def get_roo_path(self) -> InternalKey:
        return self._root_path

    def get_storage(self) -> InternalStorage:
        return self._storage

    def set_alias(self, alias: str) -> None:
        self._alias = self._alias or alias

    def get_alias(self) -> str:
        return self._alias
