from typing import IO, Any, Dict

import yaml

from pkonfig.storage.base import FileStorage


class Yaml(FileStorage):
    def load_file_content(self, handler: IO) -> Dict[str, Any]:
        return yaml.safe_load(handler)
