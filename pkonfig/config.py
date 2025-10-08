from typing import (
    Any,
    Dict,
    Generator,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from pkonfig.base_config import CachedBaseConfig
from pkonfig.errors import ConfigTypeError
from pkonfig.fields import Field, ListField
from pkonfig.storage.base import NOT_SET, BaseStorage, DictStorage


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
    kwargs : dict, optional
        Keyword arguments transformed into a DictStorage
    """

    _TYPE_FACTORIES: Dict[type[Any], Type[Field]] = {}

    def __init__(
        self,
        *storages: BaseStorage,
        alias: str = "",
        fail_fast: bool = True,
        **kwargs: Any,
    ) -> None:
        if kwargs:
            storages = (*storages, DictStorage(**kwargs))
        super().__init__(*storages, alias=alias)
        self._register_inner_configs()
        if fail_fast and self._storage:
            self.check()

    def check(self) -> None:
        """Eagerly access all declared fields to validate presence and types.

        This will also recursively validate nested Configs.
        Raises
        ------
        ConfigError
            If any required value is missing or fails type/validation in underlying fields.
        """
        for attr_name, attr in self._public_attributes():
            if isinstance(attr, Config):
                attr.check()
            else:
                getattr(self, attr_name)

    def _register_inner_configs(self) -> None:
        """Propagate storage and naming to nested Configs declared as attributes."""
        for name, config_attribute in self._public_attributes():
            if isinstance(config_attribute, Config):
                config_attribute.set_storage(self._storage)
                config_attribute.set_alias(name)
                config_attribute.set_root_path(self._root_path)

    def _public_attributes(self) -> Generator[Any, None, None]:
        """Generator that yields all attributes declared as public attributes."""
        for name, config_attribute in vars(self.__class__).items():
            if not name.startswith("_"):
                yield name, config_attribute

    @classmethod
    def register_type_factory(
        cls, python_type: type[Any], factory: Type[Field]
    ) -> None:
        cls._TYPE_FACTORIES[python_type] = factory

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        cls._materialize_annotated_fields()

    @classmethod
    def _materialize_annotated_fields(cls) -> None:
        for name, annotation in cls._get_type_hints().items():
            attribute = cls._get_attribute(name)
            if cls._should_resolve_descriptor(name, attribute):
                descriptor = cls._resolve_descriptor(annotation, attribute)
                setattr(cls, name, descriptor)
                if isinstance(descriptor, Field):
                    descriptor.__set_name__(cls, name)

    @staticmethod
    def _should_resolve_descriptor(name: str, attribute: Any) -> bool:
        """Check if an attribute should be resolved.
        Config and Field instances do not require resolution.
        """
        return not (name.startswith("_") or isinstance(attribute, (Config, Field)))

    @classmethod
    def _resolve_descriptor(cls, annotation, attribute) -> Union["Config", Field]:
        origin = get_origin(annotation)
        if origin and issubclass(origin, list):
            inner_types = get_args(annotation)
            if inner_types:
                field_cls = cls._TYPE_FACTORIES[inner_types[0]]
                cast_function = field_cls().cast
            else:
                cast_function = str  # type: ignore[assignment]
            descriptor = ListField(default=attribute, cast_function=cast_function)

        elif issubclass(annotation, Config):
            descriptor = annotation()
        elif issubclass(annotation, Field):
            descriptor = annotation(default=attribute)
        elif annotation in cls._TYPE_FACTORIES:
            descriptor = cls._TYPE_FACTORIES[annotation](default=attribute)
        else:
            raise ConfigTypeError(f"Unknown type {annotation}")
        return descriptor

    @classmethod
    def _get_type_hints(cls) -> dict[str, Any]:
        """Get type hints."""
        try:
            resolved_hints = get_type_hints(cls, include_extras=True)
        except TypeError:
            # Python < 3.9
            resolved_hints = get_type_hints(cls)
        return resolved_hints

    @classmethod
    def _get_attribute(cls, attr_name: str) -> Any:
        """Get default value."""
        return cls.__dict__.get(attr_name, NOT_SET)
