from collections import ChainMap
from inspect import isdatadescriptor
from typing import Any, Generator, Tuple

from pkonfig.storage.base import BaseStorage, InternalKey


class Config:

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
        for name, config_attribute in self._inner_configs():
            config_attribute.set_storage(self.get_storage())
            config_attribute.set_alias(name)
            config_attribute.set_root_path(self.get_roo_path())

    def _inner_configs(self) -> Generator[Tuple[str, "Config"], None, None]:
        for name, attribute in vars(self.__class__).items():
            if isinstance(attribute, Config):
                yield name, attribute

    def _config_attributes(self) -> Generator[Tuple[str, Any], None, None]:
        for attr_name, attr in filter(
            self._is_config_attribute, vars(self.__class__).items()
        ):
            yield attr_name, attr

    @staticmethod
    def _is_config_attribute(name_value: Tuple[str, Any]) -> bool:
        attr_name, attribute = name_value
        return not attr_name.startswith("_") and isdatadescriptor(attribute)

    def check(self) -> None:
        for attr_name, _ in self._config_attributes():
            getattr(self, attr_name)
        for _, inner_config in self._inner_configs():
            inner_config.check()

    def set_alias(self, alias: str) -> None:
        self._alias = self._alias or alias

    def set_root_path(self, root_path: InternalKey) -> None:
        self._root_path = (*root_path, self._alias) if self._alias else root_path

    def get_roo_path(self) -> InternalKey:
        return self._root_path

    def get_storage(self) -> ChainMap:
        return self._storage

    def set_storage(self, storage: ChainMap) -> None:
        self._storage = storage
