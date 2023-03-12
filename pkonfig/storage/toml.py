from typing import Any, BinaryIO, Dict

import tomli

from pkonfig.storage.file import MODE, FileStorage


class Toml(FileStorage):
    mode: MODE = "rb"

    def load_file_content(self, handler: BinaryIO) -> Dict[str, Any]:  # type: ignore
        return tomli.load(handler)
