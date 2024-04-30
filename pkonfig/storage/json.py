import json
from typing import IO

from pkonfig.storage.base import FileStorage


class Json(FileStorage):
    def load_file_content(self, handler: IO) -> dict:
        return json.load(handler)
