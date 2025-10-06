from pathlib import Path

import pytest

from pkonfig.storage import Ini


@pytest.fixture
def ini_file():
    return "tests/unit/test_storage/test.ini"


def test_ini_storage(ini_file: Path):
    storage = Ini(ini_file)
    assert storage[("bitbucket.org", "User")] == "hg"
    assert storage[("bitbucket.org", "ServerAliveInterval")] == "45"


def test_ini_storage_respects_defaults(ini_file):
    storage = Ini(ini_file, attr="some")
    assert storage[("attr",)] == "some"
