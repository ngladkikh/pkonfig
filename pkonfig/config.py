from collections import ChainMap
from inspect import isdatadescriptor
from typing import Any, Generator, Tuple

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
