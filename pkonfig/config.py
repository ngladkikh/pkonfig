import types
from inspect import isdatadescriptor
from typing import (
    Annotated,
    Any,
    Callable,
    ClassVar,
    Dict,
    Generator,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pkonfig.fields import Field
from pkonfig.base_config import CachedBaseConfig
from pkonfig.storage.base import BaseStorage, InternalKey

FieldFactory = Callable[[bool], Any]


class Config(CachedBaseConfig):
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
            config_attribute.set_storage(self._storage)
            config_attribute.set_alias(name)
            config_attribute.set_root_path(self._root_path)

    def _public_attributes(self) -> Generator[Any, None, None]:
        """Generator that yields all attributes declared as public attributes."""
        for name, config_attribute in vars(self.__class__).items():
            if not name.startswith("_"):
                yield name, config_attribute

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
        """Yield a (name, Config) pair for nested Config attributes."""
        for name, attribute in self._public_attributes():
            if isinstance(attribute, Config):
                yield name, attribute

    def _config_attributes(self) -> Generator[Tuple[str, Any], None, None]:
        """Yield (name, descriptor) for public Field descriptors declared on the class."""
        for attr_name, attr in self._public_attributes():
            if isdatadescriptor(attr):
                yield attr_name, attr

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

    @classmethod
    def register_type_factory(
        cls, python_type: type[Any], factory: Type[Field]
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
