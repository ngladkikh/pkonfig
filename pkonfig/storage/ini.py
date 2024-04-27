import configparser
from pathlib import Path
from typing import IO, Any, Union

from pkonfig.storage.base import FileStorage


class Ini(FileStorage):
    def __init__(  # pylint: disable=too-many-arguments
        self,
        file: Union[Path, str],
        missing_ok=False,
        allow_no_value=False,
        delimiters=("=", ":"),
        comment_prefixes=("#", ";"),
        inline_comment_prefixes=None,
        strict=True,
        empty_lines_in_values=True,
        default_section=configparser.DEFAULTSECT,
        **defaults,
    ):
        self.parser = configparser.ConfigParser(
            allow_no_value=allow_no_value,
            delimiters=delimiters,
            comment_prefixes=comment_prefixes,
            inline_comment_prefixes=inline_comment_prefixes,
            strict=strict,
            empty_lines_in_values=empty_lines_in_values,
            default_section=default_section,
        )
        super().__init__(file=file, missing_ok=missing_ok, **defaults)

    def load_file_content(self, handler: IO) -> dict[str, Any]:
        self.parser.read_string(handler.read())
        return self.parser  # type: ignore
