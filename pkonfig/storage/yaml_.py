from typing import IO, Any

import yaml

from pkonfig.storage.base import AbstractStorage, BaseFileStorage


class Yaml(BaseFileStorage, AbstractStorage):
    def load_file_content(self, handler: IO) -> dict[str, Any]:
        return yaml.safe_load(handler)
