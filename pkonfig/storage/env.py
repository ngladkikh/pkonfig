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
