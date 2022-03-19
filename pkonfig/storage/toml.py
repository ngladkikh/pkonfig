from typing import BinaryIO

import tomli

from pkonfig.storage.base import AbstractStorage, BaseFileStorage, MODE


class Toml(BaseFileStorage, AbstractStorage):
    mode: MODE = "rb"

    def load_file_content(self, handler: BinaryIO) -> None:  # type: ignore
        self.data.update(tomli.load(handler))
