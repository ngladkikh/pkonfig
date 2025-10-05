import sys
from pathlib import Path

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


def test_mypy_understands_field_typing_ok(tmp_path: Path) -> None:
    test_file = tmp_path / "snippet.py"
    test_file.write_text(SNIPPET_OK)

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

    assert exit_status == 0, f"mypy unexpectedly failed with: {stdout or stderr}"
    # Ensure there are no error lines referencing the file
    assert f"{test_file}:" not in stdout

def test_mypy_understands_field_typing_bad_assignment(tmp_path: Path) -> None:
    test_file = tmp_path / "snippet.py"
    test_file.write_text(SNIPPET_BAD_ASSIGN)

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
    assert (
        exit_status != 0
    ), "mypy should report a type error but exited successfully"
