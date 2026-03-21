import types
from collections import ChainMap
from collections.abc import MutableMapping
from typing import Any, Iterable, Union, cast, get_args, get_origin

from pydantic import AliasChoices, AliasPath, BaseModel
from pydantic.fields import FieldInfo
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from pkonfig.storage.base import BaseStorage, InternalKey

_NOT_FOUND = object()
_PKONFIG_STORAGES_KEY = "pkonfig_storages"
_PKONFIG_USE_NATIVE_SOURCES_KEY = "pkonfig_use_native_sources"


def pkonfig_settings_config(
    *storages: BaseStorage,
    use_native_sources: bool = False,
    **kwargs: Any,
) -> SettingsConfigDict:
    """Build a Pydantic Settings config with PKonfig storages attached."""

    return cast(
        SettingsConfigDict,
        {
            **kwargs,
            _PKONFIG_STORAGES_KEY: storages,
            _PKONFIG_USE_NATIVE_SOURCES_KEY: use_native_sources,
        },
    )


class PKonfigBaseSettings(BaseSettings):
    """BaseSettings with first-class support for PKonfig storages."""

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        storages = cast(
            tuple[BaseStorage, ...],
            settings_cls.model_config.get(_PKONFIG_STORAGES_KEY, ()),
        )
        if not storages:
            return (
                init_settings,
                env_settings,
                dotenv_settings,
                file_secret_settings,
            )

        sources: list[PydanticBaseSettingsSource] = [
            init_settings,
            _PKonfigSettingsSource(settings_cls, *storages),
        ]
        if settings_cls.model_config.get(_PKONFIG_USE_NATIVE_SOURCES_KEY, False):
            sources.extend((env_settings, dotenv_settings, file_secret_settings))
        return tuple(sources)


class _PKonfigSettingsSource(PydanticBaseSettingsSource):
    def __init__(self, settings_cls: type[BaseSettings], *storages: BaseStorage):
        super().__init__(settings_cls)
        storage_maps = cast(tuple[MutableMapping[InternalKey, Any], ...], storages)
        self._storage: ChainMap[InternalKey, Any] = cast(
            ChainMap[InternalKey, Any],
            ChainMap(*storage_maps),
        )
        self._case_sensitive = bool(self.config.get("case_sensitive", False))

    def get_field_value(
        self, field: FieldInfo, field_name: str
    ) -> tuple[Any, str, bool]:
        value = self._get_field_value(field_name, field, tuple())
        return value, field_name, False

    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if isinstance(value, (dict, list, tuple)):
            return value
        return super().prepare_field_value(field_name, field, value, value_is_complex)

    def __call__(self) -> dict[str, Any]:
        values: dict[str, Any] = {}
        for field_name, field in self.settings_cls.model_fields.items():
            value, key, value_is_complex = self.get_field_value(field, field_name)
            if value is _NOT_FOUND:
                continue
            values[key] = self.prepare_field_value(
                field_name, field, value, value_is_complex
            )
        return values

    def _get_field_value(
        self, field_name: str, field: FieldInfo, path_prefix: InternalKey
    ) -> Any:
        annotation = _unwrap_annotation(field.annotation)
        if _is_model(annotation):
            return self._build_model_value(annotation, field, path_prefix, field_name)

        for path in _field_lookup_paths(field_name, field, self._case_sensitive):
            full_path = (*path_prefix, *path)
            value = self._storage.get(full_path, _NOT_FOUND)
            if value is not _NOT_FOUND:
                return value
        return _NOT_FOUND

    def _build_model_value(
        self,
        model_cls: type[BaseModel],
        field: FieldInfo,
        path_prefix: InternalKey,
        field_name: str,
    ) -> Any:
        for path in _field_lookup_paths(field_name, field, self._case_sensitive):
            values: dict[str, Any] = {}
            nested_prefix = (*path_prefix, *path)
            for nested_name, nested_field in model_cls.model_fields.items():
                value = self._get_field_value(nested_name, nested_field, nested_prefix)
                if value is not _NOT_FOUND:
                    values[nested_name] = value
            if values:
                return values
        return _NOT_FOUND


def _field_lookup_paths(
    field_name: str, field: FieldInfo, case_sensitive: bool
) -> tuple[InternalKey, ...]:
    paths: list[InternalKey] = []
    for alias in _iter_aliases(field_name, field):
        normalized = tuple(
            segment if case_sensitive else segment.lower() for segment in alias
        )
        if normalized not in paths:
            paths.append(normalized)
    return tuple(paths)


def _iter_aliases(field_name: str, field: FieldInfo) -> Iterable[InternalKey]:
    aliases = (field.alias, field.validation_alias)
    found = False
    for alias in aliases:
        if alias is None:
            continue
        found = True
        yield from _expand_alias(alias)
    if not found:
        yield (field_name,)


def _expand_alias(alias: Any) -> Iterable[InternalKey]:
    if isinstance(alias, str):
        yield (alias,)
        return
    if isinstance(alias, AliasChoices):
        for choice in alias.choices:
            yield from _expand_alias(choice)
        return
    if isinstance(alias, AliasPath):
        str_segments = tuple(
            segment for segment in alias.path if isinstance(segment, str)
        )
        if str_segments:
            yield str_segments


def _unwrap_annotation(annotation: Any) -> Any:
    while True:
        origin = get_origin(annotation)
        if origin is None:
            return annotation
        if origin in (Union, types.UnionType):
            args = tuple(
                arg for arg in get_args(annotation) if arg is not types.NoneType
            )
            if len(args) == 1:
                annotation = args[0]
                continue
        if str(origin) == "typing.Annotated":
            annotation = get_args(annotation)[0]
            continue
        return annotation


def _is_model(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)
