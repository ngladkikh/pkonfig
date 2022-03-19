from typing import IO

import yaml

from pkonfig.storage.base import AbstractStorage, BaseFileStorage


class Yaml(BaseFileStorage, AbstractStorage):
    def load_file_content(self, handler: IO) -> None:
        self.data.update(yaml.safe_load(handler))
