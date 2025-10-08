from abc import ABC, abstractmethod
from collections.abc import Mapping
from pathlib import Path
from typing import IO, Any, Iterator, Tuple, Union

InternalKey = Tuple[str, ...]
DEFAULT_PREFIX = "APP"
DEFAULT_DELIMITER = "_"
NOT_SET = "NOT_SET"


class BaseStorage(ABC):
    """Plain config data storage"""

    def __init__(self) -> None:
        self._actual_storage: dict[InternalKey, Any] = {}

    def __getitem__(self, key: InternalKey) -> Any:
        return self._actual_storage[key]

    def __iter__(self) -> Iterator[InternalKey]:
        return iter(self._actual_storage)

    def get(self, key: InternalKey, default: Any) -> Any:
        if key in self._actual_storage:
            return self._actual_storage[key]
        return default

    def __repr__(self) -> str:
        return self.__class__.__name__


class FlattenedStorageMixin(ABC):
    _actual_storage: dict[InternalKey, Any]

    def flatten(
        self, multilevel_storage: Mapping[str, Any], path_key: InternalKey
    ) -> None:
        for key, value in multilevel_storage.items():
            current_path = self._build_path_key(path_key, key)
            if isinstance(value, Mapping):
                self.flatten(value, current_path)
            else:
                self._actual_storage[current_path] = value

    @staticmethod
    def _build_path_key(
        path_key: InternalKey, key: Union[str, Tuple[str, ...]]
    ) -> InternalKey:
        if isinstance(key, tuple):
            return *path_key, *key
        return *path_key, key


class FileStorage(BaseStorage, FlattenedStorageMixin, ABC):
    mode = "r"

    def __init__(
        self,
        file: Union[Path, str],
        missing_ok: bool = False,
        **defaults,
    ) -> None:
        super().__init__()
        self.file = file if isinstance(file, Path) else Path(file)
        self.missing_ok = missing_ok
        self.flatten(defaults, tuple())
        self.load()

    def __repr__(self) -> str:
        return str(self.file.absolute())

    def load(self) -> None:
        if self.file.exists() and self.file.is_file():
            self.flatten(self._load(), tuple())
        else:
            if not self.missing_ok:
                raise FileNotFoundError()

    def _load(self) -> Mapping[str, Any]:
        with open(self.file, self.mode) as fh:  # pylint: disable=unspecified-encoding
            return self.load_file_content(fh)

    @abstractmethod
    def load_file_content(self, handler: IO) -> Mapping[str, Any]:
        """Load file content and return a mapping from keys to values."""


class DictStorage(BaseStorage, FlattenedStorageMixin):

    def __init__(self, **defaults) -> None:
        super().__init__()
        self.flatten(defaults, tuple())

    def __getitem__(self, key: InternalKey) -> Any:
        return self._actual_storage[key]

    def __repr__(self) -> str:
        return str(self._actual_storage)


class EnvKeyConverter:

    def __init__(
        self, delimiter: str = DEFAULT_DELIMITER, prefix: str = DEFAULT_PREFIX
    ) -> None:
        self.delimiter = delimiter
        self.prefix = prefix

    def to_key(self, internal_key: InternalKey) -> str:
        if self.prefix:
            return self.delimiter.join((self.prefix, *internal_key))
        return self.delimiter.join(internal_key)
