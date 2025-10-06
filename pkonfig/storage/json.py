import json
from typing import IO

from pkonfig.storage.base import FileStorage


class Json(FileStorage):
    """Read configuration from a JSON document.

    The file is decoded with ``json.load`` and then flattened into the
    internal key map.
    """

    def load_file_content(self, handler: IO) -> dict:
        return json.load(handler)
