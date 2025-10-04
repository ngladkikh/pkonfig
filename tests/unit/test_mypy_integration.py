import sys
from pathlib import Path

import pytest

from mypy import api as mypy_api


SNIPPET_OK = """
from pathlib import Path
from pkonfig.config import Config
from pkonfig.fields import Field, Int, Str, Bool, File, Bytes
from pkonfig.storage.env import Env

class App(Config):
    host: str = Str("127.0.0.1")
    port: int = Int(8000)
    debug: bool = Bool(False)
    path: Path = File()
    bytes_: bytes = Bytes()

cfg = App(Env(prefix="APP"))

# Static types must be what we annotated above
host_ok: str = cfg.host
port_ok: int = cfg.port
flag_ok: bool = cfg.debug
"""

SNIPPET_BAD_ASSIGN = """
from pkonfig.config import Config
from pkonfig.fields import Int

class App(Config):
    port: int = Int(8000)

cfg = App()
# Intentional: assigning int-typed attribute to a str variable must be a type error
bad: str = cfg.port  # E: Incompatible types in assignment
"""


@pytest.mark.parametrize(
    "code, expect_ok",
    [
        (SNIPPET_OK, True),
        (SNIPPET_BAD_ASSIGN, False),
    ],
)
def test_mypy_understands_field_typing(tmp_path: Path, code: str, expect_ok: bool) -> None:
    test_file = tmp_path / "snippet.py"
    test_file.write_text(code)

    # Run mypy against the snippet file. Use flags for deterministic output.
    stdout, stderr, exit_status = mypy_api.run(
        [
            str(test_file),
            "--no-incremental",
            "--show-error-codes",
            "--hide-error-context",
            "--no-error-summary",
            "--python-version",
            f"{sys.version_info.major}.{sys.version_info.minor}",
        ]
    )

    if expect_ok:
        assert exit_status == 0, f"mypy unexpectedly failed with: {stdout or stderr}"
        # Ensure there are no error lines referencing the file
        assert f"{test_file}:" not in stdout
    else:
        assert exit_status != 0, "mypy should report a type error but exited successfully"
        # mypy reports error lines prefixed with the file path
        assert f"{test_file}:" in stdout
        # Optional sanity check: the error should be about incompatible assignment
        assert "[assignment]" in stdout or "Incompatible types" in stdout
