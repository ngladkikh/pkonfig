from pathlib import Path
from typing import IO, Mapping, Tuple, Union

from pkonfig.storage.base import (
    DEFAULT_DELIMITER,
    DEFAULT_PREFIX,
    FileStorage,
    InternalKey,
)


class DotEnv(FileStorage):
    """Load configuration from a classic ``.env`` file.

    Lines are parsed into key/value pairs with optional prefix trimming before
    being normalized into the internal key format.
    """

    def __init__(
        self,
        file: Union[Path, str],
        delimiter=DEFAULT_DELIMITER,
        prefix=DEFAULT_PREFIX,
        missing_ok: bool = False,
        **defaults,
    ):
        self.delimiter = delimiter
        self.prefix = prefix
        super().__init__(file, missing_ok, **defaults)

    def load_file_content(self, handler: IO) -> Mapping:
        res = {}
        for line in filter(self.filter, handler.readlines()):
            keys, value = self.split(line)
            res[keys] = value
        return res

    def split(self, param_line: str) -> Tuple[Tuple[str, ...], str]:
        """Splits string on key and value, removes prefix and spaces"""
        key: str
        key, value = param_line.split("=", maxsplit=1)
        key = key.strip()
        if self.prefix:
            key = key.replace(self.prefix + self.delimiter, "")
        keys = key.lower().split(self.delimiter)
        return tuple(keys), value.strip()

    @staticmethod
    def filter(param_line: str) -> bool:
        return len(param_line) > 2 and (not param_line.startswith(("#", "//")))

    def __getitem__(self, key: InternalKey):
        try:
            return super().__getitem__(key)
        except KeyError:
            lowered = tuple(segment.lower() for segment in key)
            return super().__getitem__(lowered)

    def get(self, key: InternalKey, default):
        if key in self._actual_storage:
            return self._actual_storage[key]
        lowered = tuple(segment.lower() for segment in key)
        if lowered in self._actual_storage:
            return self._actual_storage[lowered]
        return default

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, tuple):
            return False
        if key in self._actual_storage:
            return True
        lowered = tuple(segment.lower() for segment in key if isinstance(segment, str))
        return lowered in self._actual_storage
