from collections import ChainMap
from inspect import isdatadescriptor
from typing import Any, ClassVar, Generator, Tuple, get_args, get_origin, get_type_hints

from pkonfig.storage.base import BaseStorage, InternalKey


class Config:
    """Base configuration container.

    Define your configuration by subclassing Config and declaring Field descriptors
    (from pkonfig.fields) as class attributes, or nested Configs for grouping.

    Parameters
    ----------
    *storages : BaseStorage
        One or more storage backends to read configuration values from, in
        priority order (leftmost has highest priority).
    alias : str, optional
        Optional alias for this config used to build nested keys, by default "".
    fail_fast : bool, optional
        If True (default), access all declared fields during initialization to
        ensure required values are present and types/validators pass. If False,
        validation happens lazily on first access.
    """

    def __init__(
        self,
        *storages: BaseStorage,
        alias: str = "",
        fail_fast: bool = True,
    ) -> None:
        self._storage = ChainMap(*storages)  # type:ignore
        self._alias = alias
        self._root_path: InternalKey = (alias,) if alias else tuple()
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
    def _materialize_annotated_fields(cls) -> None:
        """Instantiate Field descriptors for bare type-hinted attributes."""
        # TODO: Fix linting warnings
        # pylint: disable=R0914,C0415
        raw_annotations = cls.__dict__.get("__annotations__", {})
        if not raw_annotations:
            return

        try:
            resolved_hints = get_type_hints(cls, include_extras=True)
        except TypeError:
            # Fallback on Python <3.11 where include_extras is not supported.
            resolved_hints = get_type_hints(cls)

        # Late import to avoid circular dependency during module import.
        from pathlib import Path
        from typing import Annotated, Union

        from pkonfig.fields import Bool, Field, Float, Int, PathField, Str

        type_map = {
            str: lambda nullable: Str(nullable=nullable),
            int: lambda nullable: Int(nullable=nullable),
            float: lambda nullable: Float(nullable=nullable),
            bool: lambda nullable: Bool(nullable=nullable),
            Path: lambda nullable: PathField(nullable=nullable, missing_ok=True),
        }

        for name in raw_annotations:
            # Skip attributes that already provide a descriptor/value.
            if name in cls.__dict__ and isinstance(cls.__dict__[name], Field):
                continue
            if name in cls.__dict__ and not isinstance(cls.__dict__[name], Field):
                continue

            annotation = resolved_hints.get(name, raw_annotations[name])
            target_type, nullable = cls._resolve_annotation_target(
                annotation, Annotated, Union
            )
            if target_type is None:
                continue

            field_factory = type_map.get(target_type)
            if field_factory is None:
                continue

            descriptor = field_factory(nullable)
            setattr(cls, name, descriptor)
            descriptor.__set_name__(cls, name)  # type: ignore

    @staticmethod
    def _resolve_annotation_target(  # pylint: disable=R0911
        annotation: Any, annotated_type: Any, union_type: Any
    ) -> Tuple[Any, bool]:
        """Return the underlying Python type and nullability for an annotation."""

        origin = get_origin(annotation)

        if origin is annotated_type:
            inner_annotation = get_args(annotation)[0]
            return Config._resolve_annotation_target(
                inner_annotation, annotated_type, union_type
            )

        if origin is union_type or getattr(origin, "__name__", None) == "UnionType":
            args = tuple(arg for arg in get_args(annotation) if arg is not type(None))
            if len(args) == 1 and len(get_args(annotation)) == 2:
                inner_type, _ = Config._resolve_annotation_target(
                    args[0], annotated_type, union_type
                )
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
        """Return True if attribute looks like a public Field descriptor.

        An attribute is considered a config attribute if it does not start with an
        underscore and is a data descriptor (i.e., implements the descriptor protocol).
        """
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

    def __init_subclass__(cls, **kwargs) -> None:  # type: ignore[override]
        super().__init_subclass__(**kwargs)
        cls._materialize_annotated_fields()
