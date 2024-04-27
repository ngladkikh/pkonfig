import sys
from typing import Any, BinaryIO, Dict

from pkonfig.storage.base import FileStorage


def _load(file_handler: BinaryIO) -> Dict[str, Any]:
    if sys.version_info >= (3, 11):
        import tomllib  # pylint: disable=import-outside-toplevel

        return tomllib.load(file_handler)
    import tomli  # pylint: disable=import-outside-toplevel

    return tomli.load(file_handler)


class Toml(FileStorage):
    mode = "rb"

    def load_file_content(self, handler: BinaryIO) -> Dict[str, Any]:  # type: ignore
        return _load(handler)
