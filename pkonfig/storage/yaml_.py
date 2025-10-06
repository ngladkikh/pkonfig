from typing import IO, Any, Dict

import yaml

from pkonfig.storage.base import FileStorage


class Yaml(FileStorage):
    """Read configuration from a YAML document with ``yaml.safe_load``.

    Nested mappings are flattened into dotted keys to match other storages.
    """

    def load_file_content(self, handler: IO) -> Dict[str, Any]:
        return yaml.safe_load(handler)
