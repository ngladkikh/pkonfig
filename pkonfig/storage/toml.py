from typing import BinaryIO

import tomli

from pkonfig.storage.base import AbstractStorage, BaseFileStorageMixin


class Toml(BaseFileStorageMixin, AbstractStorage):
    mode = "rb"

    def load_file_content(self, handler: BinaryIO) -> None:
        self.data.update(tomli.load(handler))
