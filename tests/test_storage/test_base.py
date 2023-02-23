import json
from pathlib import Path

import pytest

from base import Storage
from pkonfig.storage import (
    Env,
    Json,
    Ini,
)


def test_env_config_outer(monkeypatch):
    monkeypatch.setenv("APP_KEY", "VALUE")
    storage = Env(delimiter="_")
    assert storage["key"] == "VALUE"


def test_default_values_added(monkeypatch):
    monkeypatch.setenv("APP_SOME", "VALUE")
    storage = Env(delimiter="_", foo="baz", fiz="buz", some="ignored")
    assert storage[("SOME",)] == "VALUE"
    assert storage[("foo",)] == "baz"
    assert storage[("fiz",)] == "buz"


def test_second_level_variable(monkeypatch):
    monkeypatch.setenv("APP_KEY1_KEY2", "VALUE2")
    storage = Env(delimiter="_", prefix="APP")
    assert storage[("key1", "key2")] == "VALUE2"


def test_no_prefix_gets_all(monkeypatch):
    monkeypatch.setenv("SOME", "VALUE")
    storage = Env(delimiter="_", prefix="")
    assert storage[("some",)] == "VALUE"


def test_file_storage_read_file(storage_file, file_storage_cls):
    storage = file_storage_cls(storage_file)
    assert "CONTENT" in storage._data


def test_file_storage_missing_raises(file_storage_cls):
    with pytest.raises(FileNotFoundError):
        file_storage_cls(Path("test"))


def test_file_storage_missing_ok(file_storage_cls):
    storage = file_storage_cls(Path("test"), missing_ok=True)
    assert storage._data == {}


@pytest.fixture
def storage_file(tmp_path):
    file = tmp_path / "test"
    open(file, "w").close()
    yield file


def test_json_storage(json_configs, file):
    storage = Json(file)
    for key, value in json_configs.items():
        assert storage[(key,)] == value


@pytest.fixture
def json_configs(file):
    data = {
        "str": "value",
        "int": 1,
        "float": 1/3,
        "bool": True,
    }
    with open(file, "w") as fh:
        json.dump(data, fh)
    yield data


def test_ini_storage(ini_file):
    storage = Ini(ini_file)
    assert storage[("BITBUCKET.ORG", "USER")] == "hg"
    assert storage[("BITBUCKET.ORG", "SERVERALIVEINTERVAL")] == "45"


def test_ini_storage_respects_defaults(ini_file):
    storage = Ini(ini_file, attr="some")
    assert storage[("attr",)] == "some"


@pytest.fixture
def ini_file():
    return "tests/test_storage/test.ini"


@pytest.fixture
def file(tmp_path):
    return tmp_path / "test_config"


def test_multilevel(monkeypatch, ini_file, json_configs, file):
    monkeypatch.setenv("APP__STR", "env")
    monkeypatch.setenv("APP__BITBUCKET.ORG__USER", "foo")
    storage = Storage(
        Env(),
        Ini(ini_file),
        Json(file),
        fiz="buz",
    )
    assert storage[("str",)] == "env"
    assert storage[("bitbucket.org", "user")] == "foo"
    assert storage[("int",)] == 1
    assert storage[("BITBUCKET.ORG", "SERVERALIVEINTERVAL")] == "45"
    assert storage[("fiz",)] == "buz"
