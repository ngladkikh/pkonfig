import os
from typing import Any

from pkonfig.storage.base import (
    DEFAULT_DELIMITER,
    DEFAULT_PREFIX,
    BaseStorage,
    DictStorage,
    EnvKeyConverter,
    InternalKey,
)


class Env(BaseStorage):
    """Read configuration values from environment variables.

    Values are looked up using an optional prefix/delimiter pairing. Defaults
    fall back to an in-memory mapping if a given key is not present in the
    environment.
    """

    def __init__(
        self, delimiter=DEFAULT_DELIMITER, prefix=DEFAULT_PREFIX, **defaults
    ) -> None:
        super().__init__()
        self._converter = EnvKeyConverter(prefix=prefix, delimiter=delimiter)
        self._default = DictStorage(**defaults)

    def __getitem__(self, key: InternalKey) -> Any:
        str_key = self._converter.to_key(key)
        upper_str_key = str_key.upper()
        if upper_str_key in os.environ:
            return os.environ[upper_str_key]

        if str_key in os.environ:
            return os.environ[str_key]

        return self._default[key]

    def get(self, key: InternalKey, default: Any) -> Any:
        str_key = self._converter.to_key(key)
        upper_str_key = str_key.upper()
        if upper_str_key in os.environ:
            return os.environ[upper_str_key]

        if str_key in os.environ:
            return os.environ[str_key]

        return self._default.get(key, default)

    def __repr__(self) -> str:
        return "EnvVars"

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, tuple):
            return False
        str_key = self._converter.to_key(key)
        if str_key.upper() in os.environ:
            return True
        if str_key in os.environ:
            return True
        return key in self._default
