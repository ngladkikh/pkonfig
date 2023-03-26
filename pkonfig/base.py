from abc import ABC, ABCMeta, abstractmethod
from collections import ChainMap
from inspect import isclass, isdatadescriptor
from typing import Any, List, MutableMapping
from typing import (
    Dict,
    Generic,
    Iterator,
    Mapping,
    Optional,
    Reversible,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

InternalKey = Tuple[str, ...]
InternalStorage = MutableMapping[InternalKey, Any]
NOT_SET = object()
T = TypeVar("T")


class ConfigError(Exception):
    """Configuration error"""


class ConfigValueNotFoundError(ConfigError):
    """Failed to find value in given storage(s)"""


class ConfigTypeError(ConfigError):
    """Value has wrong type"""


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
        value = self._cast(value)
        self._validate(value)
        path = self.get_path(instance)
        self._cache[path] = value

    def __get__(self, instance: "BaseConfig", _=None) -> Union[T, object]:
        path = self.get_path(instance)
        value = NOT_SET if self.no_cache else self._cache.get(path, NOT_SET)
        if value is NOT_SET:
            value = self.get_from_storage(instance)
            if value is not None:
                value = self._cast(value)
                self._validate(value)
            else:
                if not self.nullable:
                    raise ConfigTypeError(f"{self.path} value is None")
            self._cache[path] = value
        return value

    def get_path(self, instance: "BaseConfig") -> InternalKey:
        return tuple(instance.get_roo_path() + (self.alias,))

    def get_from_storage(self, instance: "BaseConfig") -> Any:
        storage = instance.get_storage()
        path = self.get_path(instance)
        if path in storage:
            return storage[path]
        if self.default is not NOT_SET:
            return self.default
        raise ConfigValueNotFoundError({".".join(path)})

    def _cast(self, value: Any) -> T:
        try:
            return self.cast(value)
        except (ValueError, TypeError) as exc:
            raise ConfigTypeError(f"{value} casting error") from exc

    @abstractmethod
    def cast(self, value: Any) -> T:
        pass

    def _validate(self, value: Any) -> None:
        try:
            return self.validate(value)
        except TypeError as exc:
            raise ConfigTypeError(f"{value} validation error") from exc

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


class BaseStorage(MutableMapping, ABC):
    """Plain config data storage"""

    @abstractmethod
    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        ...

    def __iter__(self) -> Iterator[Any]:
        return iter(())

    def __setitem__(self, __k: Any, __v: Any) -> None:
        pass

    def __delitem__(self, __v: Any) -> None:
        pass


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
            else:
                internal_storages.append(Storage(s))
        self._storage = ChainMap(*internal_storages)
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
