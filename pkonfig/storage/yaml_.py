from typing import IO

import yaml

from pkonfig.storage.base import AbstractStorage, BaseFileStorageMixin


class Yaml(BaseFileStorageMixin, AbstractStorage):
    def load_file_content(self, handler: IO) -> None:
        self.data.update(yaml.load(handler))
