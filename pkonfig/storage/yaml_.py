from typing import IO, Any

import yaml

from pkonfig.storage.file import FileStorage


class Yaml(FileStorage):
    def load_file_content(self, handler: IO) -> dict[str, Any]:
        return yaml.safe_load(handler)
