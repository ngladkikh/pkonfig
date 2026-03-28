from pathlib import Path
from typing import IO, Iterator

from pkonfig.storage.base import FileStorage


class SecretFile(FileStorage):
    """Load secrets from a single file or from files in a directory.

    Each file becomes a separate config entry where the filename stem is used as
    the key and the raw file contents are used as the value.
    """

    def load(self) -> None:
        if self.file.is_file():
            self._actual_storage[(self.file.stem,)] = self._load_secret(self.file)
            return

        if self.file.is_dir():
            for path in self._iter_secret_files():
                self._actual_storage[(path.stem,)] = self._load_secret(path)
            return

        if not self.missing_ok:
            raise FileNotFoundError()

    def _iter_secret_files(self) -> Iterator[Path]:
        for path in sorted(self.file.iterdir()):
            if path.is_file():
                yield path

    @staticmethod
    def _load_secret(path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def load_file_content(self, handler: IO) -> dict[str, str]:
        return {self.file.stem: handler.read()}
