import os
from typing import Any, Optional, Tuple

from pkonfig.base import BaseStorage, InternalKey, Storage

DEFAULT_PREFIX = "APP"
DEFAULT_DELIMITER = "_"


class EnvMixin:
    # pylint: disable=too-few-public-methods

    def __init__(
        self, delimiter=DEFAULT_DELIMITER, prefix=Optional[DEFAULT_PREFIX]
    ) -> None:
        self.prefix = prefix
        self.delimiter = delimiter

    def to_key(self, internal_key: InternalKey) -> str:
        if self.prefix:
            return self.delimiter.join((self.prefix, *internal_key))
        return self.delimiter.join(internal_key)


class Env(BaseStorage, EnvMixin):
    def __init__(
        self, delimiter=DEFAULT_DELIMITER, prefix=DEFAULT_PREFIX, **defaults
    ) -> None:
        super().__init__(delimiter=delimiter, prefix=prefix)
        self.default = Storage(defaults)

    def __getitem__(self, key: Tuple[str, ...]) -> Any:
        str_key = self.to_key(key)
        upper_str_key = str_key.upper()
        if upper_str_key in os.environ:
            return os.environ[upper_str_key]

        if str_key in os.environ:
            return os.environ[str_key]

        return self.default[key]

    def __len__(self) -> int:
        return len(os.environ)
