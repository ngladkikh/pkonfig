from collections import ChainMap
from typing import Any

from pkonfig.storage.base import BaseStorage, InternalKey, NOT_SET


class BaseConfig:
    """Base class encapsulating config storage interaction logic."""

    def __init__(self, *storages: BaseStorage, alias: str = "") -> None:
        self._storage = ChainMap(*storages)  # type: ignore
        self._alias = alias
        self._root_path: InternalKey = (alias,) if alias else tuple()

    def __getitem__(self, item: InternalKey) -> Any:
        """Get item from storage."""
        return self._storage.get(item, NOT_SET)

    def __contains__(self, item: InternalKey) -> bool:
        """Check if an item is in storage."""
        return item in self._storage

    def set_root_path(self, root_path: InternalKey) -> None:
        """Set the root path prefix used to build full keys for nested configs."""
        self._root_path = (*root_path, self._alias) if self._alias else root_path

    def set_storage(self, storage: ChainMap) -> None:
        """Set the storage ChainMap. Used internally when nesting configs."""
        self._storage = storage
