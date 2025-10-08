import types
from collections import ChainMap
from inspect import isdatadescriptor
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Tuple,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pkonfig.base_config import BaseConfig
from pkonfig.storage.base import BaseStorage, InternalKey

FieldFactory = Callable[[bool], Any]


class Config(BaseConfig):
    """Base configuration container.

    Define your configuration by subclassing Config and declaring Field descriptors
    (from pkonfig.fields) as class attributes or nested Configs for grouping.

    Parameters
    ----------
    *storages : BaseStorage
        One or more storage backends to read configuration values from, in
        priority order (leftmost has the highest priority).
    alias : str, optional
        Optional alias for this config used to build nested keys, by default "".
    fail_fast : bool, optional
        If True (default), access all declared fields during initialization to
        ensure required values are present, and types/validators pass. If False,
        validation happens lazily on first access.
    """

    _TYPE_FACTORIES: Dict[type[Any], FieldFactory] = {}

    def __init__(self, *storages: BaseStorage, alias: str = "", fail_fast: bool = True) -> None:
        super().__init__(*storages, alias=alias)
        self._register_inner_configs()
        if fail_fast and self._storage:
            self.check()

    def _register_inner_configs(self) -> None:
        """Propagate storage and naming to nested Configs declared as attributes."""
        for name, config_attribute in self._inner_configs():
            config_attribute.set_storage(self.get_storage())
            config_attribute.set_alias(name)
            config_attribute.set_root_path(self.get_roo_path())

    @classmethod
    def _resolve_annotation_target(  # pylint: disable=too-many-return-statements
        cls, annotation: Any
    ) -> Tuple[Any, bool]:
        """Return the underlying Python type and nullability for an annotation."""

        origin = get_origin(annotation)

        if origin is Annotated:
            inner_annotation = get_args(annotation)[0]
            return cls._resolve_annotation_target(inner_annotation)

        union_types = (Union, getattr(types, "UnionType", Union))
        if origin in union_types:
            args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
            if len(args) == 1 and len(get_args(annotation)) == 2:
                inner_type, _ = cls._resolve_annotation_target(args[0])
                return inner_type, True
            return None, False

        if origin is ClassVar:
            return None, False

        if isinstance(annotation, str):
            return None, False

        if isinstance(annotation, type) and issubclass(annotation, Config):
            return None, False

        if isinstance(annotation, type):
            return annotation, False

        return None, False

    def _inner_configs(self) -> Generator[Tuple[str, "Config"], None, None]:
        """Yield pairs of (name, Config) for nested Config attributes."""
        for name, attribute in vars(self.__class__).items():
            if isinstance(attribute, Config):
                yield name, attribute

    def _config_attributes(self) -> Generator[Tuple[str, Any], None, None]:
        """Yield (name, descriptor) for public Field descriptors declared on the class."""
        for attr_name, attr in filter(
            self._is_config_attribute, vars(self.__class__).items()
        ):
            yield attr_name, attr

    @staticmethod
    def _is_config_attribute(name_value: Tuple[str, Any]) -> bool:
        """Return True if attribute looks like a public Field descriptor."""
        attr_name, attribute = name_value
        return not attr_name.startswith("_") and isdatadescriptor(attribute)

    def check(self) -> None:
        """Eagerly access all declared fields to validate presence and types.

        This will also recursively validate nested Configs.
        Raises
        ------
        ConfigError
            If any required value is missing or fails type/validation in underlying fields.
        """
        for attr_name, _ in self._config_attributes():
            getattr(self, attr_name)
        for _, inner_config in self._inner_configs():
            inner_config.check()

    def set_alias(self, alias: str) -> None:
        """Set alias if it wasn't already defined."""
        self._alias = self._alias or alias

    def set_root_path(self, root_path: InternalKey) -> None:
        """Set the root path prefix used to build full keys for nested configs."""
        self._root_path = (*root_path, self._alias) if self._alias else root_path

    def get_roo_path(self) -> InternalKey:
        """Return the root path (tuple of key segments) for this Config."""
        return self._root_path

    def get_storage(self) -> ChainMap:
        """Return the combined ChainMap of storages used by this Config."""
        return self._storage

    def set_storage(self, storage: ChainMap) -> None:
        """Set the storage ChainMap. Used internally when nesting configs."""
        self._storage = storage

    @classmethod
    def register_type_factory(
        cls, python_type: type[Any], factory: FieldFactory
    ) -> None:
        cls._TYPE_FACTORIES[python_type] = factory

    @classmethod
    def _materialize_annotated_fields(cls) -> None:
        raw_annotations = cls.__dict__.get("__annotations__", {})
        if not raw_annotations:
            return

        try:
            resolved_hints = get_type_hints(cls, include_extras=True)
        except TypeError:
            resolved_hints = get_type_hints(cls)

        for name in raw_annotations:
            if name in cls.__dict__:
                # Attribute already provided explicitly; do not replace it.
                continue

            annotation = resolved_hints.get(name, raw_annotations[name])
            target_type, nullable = cls._resolve_annotation_target(annotation)
            if target_type is None:
                continue

            factory = cls._TYPE_FACTORIES.get(target_type)
            if factory is None:
                continue

            descriptor = factory(nullable)
            setattr(cls, name, descriptor)
            if hasattr(descriptor, "__set_name__"):
                descriptor.__set_name__(cls, name)

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        cls._materialize_annotated_fields()
