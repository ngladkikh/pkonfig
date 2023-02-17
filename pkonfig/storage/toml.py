from typing import BinaryIO, Any

import tomli

from pkonfig.storage.base import AbstractStorage, BaseFileStorage, MODE


class Toml(BaseFileStorage, AbstractStorage):
    mode: MODE = "rb"

    def load_file_content(self, handler: BinaryIO) -> dict[str, Any]:   # type: ignore
        return tomli.load(handler)
