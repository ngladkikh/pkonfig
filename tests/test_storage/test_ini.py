import pytest

from pkonfig import Ini


@pytest.fixture
def ini_file():
    return "tests/test_storage/test.ini"


def test_ini_storage(ini_file):
    storage = Ini(ini_file)
    assert storage[("bitbucket.org", "user")] == "hg"
    assert storage[("bitbucket.org", "serveraliveinterval")] == "45"


def test_ini_storage_respects_defaults(ini_file):
    storage = Ini(ini_file, attr="some")
    assert storage[("attr",)] == "some"
