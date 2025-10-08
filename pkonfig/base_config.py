from collections import ChainMap
from typing import Any, Dict

from pkonfig.errors import ConfigValueNotFoundError
from pkonfig.storage.base import NOT_SET, BaseStorage, InternalKey


class BaseConfig:
    """Base class encapsulating config storage interaction logic."""

    def __init__(self, *storages: BaseStorage, alias: str = "") -> None:
        self._storage = ChainMap(*storages)  # type: ignore
        self._alias = alias
        self._root_path: InternalKey = (alias,) if alias else tuple()

    def internal_key(self, item: str) -> InternalKey:
        """Prepend an item with self._root_path."""
        return *self._root_path, item

    def __getitem__(self, item: str) -> Any:
        """Get item from storage."""
        path = self.internal_key(item)
        if path not in self._storage:
            raise ConfigValueNotFoundError(
                f"'{'.'.join(path)}' not found in {self._storage.maps}"
            )
        return self._storage[path]

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item from storage."""
        self._storage[self.internal_key(key)] = value

    def get(self, item: str, default: Any = NOT_SET) -> Any:
        """Get item from storage or return default."""
        return self._storage.get(self.internal_key(item), default)

    def __contains__(self, item: InternalKey) -> bool:
        """Check if an item is in storage."""
        return item in self._storage

    def set_root_path(self, root_path: InternalKey) -> None:
        """Set the root path prefix used to build full keys for nested configs."""
        self._root_path = (*root_path, self._alias) if self._alias else root_path

    def set_storage(self, storage: ChainMap) -> None:
        """Set the storage ChainMap. Used internally when nesting configs."""
        self._storage = storage

    def set_alias(self, alias: str) -> None:
        """Set alias if it wasn't already defined."""
        self._alias = self._alias or alias


class CachedBaseConfig(BaseConfig):
    """Base config with a local cache."""

    def __init__(self, *storages: BaseStorage, alias: str = "") -> None:
        super().__init__(*storages, alias=alias)
        self.__cache: Dict[str, Any] = {}

    def __getitem__(self, item: str) -> Any:
        """Get item from storage."""
        if item in self.__cache:
            return self.__cache[item]
        value = super().__getitem__(item)
        self.__cache[item] = value
        return value

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item from storage."""
        self.__cache[key] = value

    def get(self, item: str, default: Any = NOT_SET) -> Any:
        """Get item from storage or return default."""
        if item in self.__cache:
            return self.__cache[item]
        value = super().get(item, default)
        self.__cache[item] = value
        return value
