from typing import BinaryIO

import tomli

from pkonfig.storage.base import AbstractStorage, BaseFileStorageMixin, MODE


class Toml(BaseFileStorageMixin, AbstractStorage):
    mode: MODE = "rb"

    def load_file_content(self, handler: BinaryIO) -> None:
        self.data.update(tomli.load(handler))
