from typing import BinaryIO, Any

import tomli

from pkonfig.storage.file import FileStorage
from storage.file import MODE


class Toml(FileStorage):
    mode: MODE = "rb"

    def load_file_content(self, handler: BinaryIO) -> dict[str, Any]:  # type: ignore
        return tomli.load(handler)
