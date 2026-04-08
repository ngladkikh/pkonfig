import json
from collections.abc import Mapping
from pathlib import Path
from typing import IO, Any, Iterator, Optional

from pkonfig.storage.base import FileStorage


class SecretFile(FileStorage):
    """Load secrets from a single file or from files in a directory.

    Each file becomes a separate config entry where the filename stem is used as
    the key and the raw file contents are used as the value.
    """

    def load(self) -> None:
        if self.file.is_file():
            self._load_secret_file(self.file)
            return

        if self.file.is_dir():
            for path in self._iter_secret_files():
                self._load_secret_file(path)
            return

        if not self.missing_ok:
            raise FileNotFoundError()

    def _iter_secret_files(self) -> Iterator[Path]:
        for path in sorted(self.file.iterdir()):
            if path.is_file():
                yield path

    def _load_secret_file(self, path: Path) -> None:
        secret = path.read_text(encoding="utf-8")
        vault_secret = self._extract_vault_secret(secret)
        if vault_secret is not None:
            self.flatten(vault_secret, tuple())
            return
        self._actual_storage[(path.stem,)] = secret

    @classmethod
    def _extract_vault_secret(cls, secret: str) -> Optional[Mapping[str, Any]]:
        try:
            payload = json.loads(secret)
        except json.JSONDecodeError:
            return None

        if not isinstance(payload, Mapping):
            return None

        data = payload.get("data")
        if not isinstance(data, Mapping):
            return None

        nested_data = data.get("data")
        if isinstance(nested_data, Mapping) and "metadata" in data:
            return nested_data

        if cls._looks_like_vault_envelope(payload):
            return data

        return None

    @staticmethod
    def _looks_like_vault_envelope(payload: Mapping[str, Any]) -> bool:
        return any(
            key in payload
            for key in (
                "request_id",
                "lease_id",
                "renewable",
                "lease_duration",
                "wrap_info",
                "warnings",
                "auth",
            )
        )

    def load_file_content(self, handler: IO) -> dict[str, str]:
        return {self.file.stem: handler.read()}
