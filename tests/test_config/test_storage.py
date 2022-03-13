from pathlib import Path
from typing import Any, Dict, IO

import pytest

from pkonfig.storage import (
    Env,
    BaseFileStorageMixin,
    PlainStructureParserMixin,
)


def test_env_config_outer(monkeypatch):
    monkeypatch.setenv("APP_KEY", "VALUE")
    storage = Env()
    assert storage["key"] == "VALUE"


@pytest.fixture
def storage():
    return Env()


def test_second_level_variable(monkeypatch):
    monkeypatch.setenv("APP_KEY1_KEY2", "VALUE2")
    storage = Env()
    assert storage["key1"]["key2"] == "VALUE2"


def test_multiple_third_level(monkeypatch):
    monkeypatch.setenv("APP_A_B_KEY1", "VALUE1")
    monkeypatch.setenv("APP_A_B_KEY2", "VALUE2")
    storage = Env()
    assert storage["a"]["b"]["key1"] == "VALUE1"
    assert storage["a"]["b"]["key2"] == "VALUE2"


@pytest.mark.parametrize(
    "key,levels",
    [("APP_A_", ["a"]), ("APP_A__B", ["a", "b"])]
)
def test_empty_values_skipped(key, levels, monkeypatch):
    monkeypatch.setenv(key, "VALUE")
    storage = Env()
    for key in levels:
        storage = storage[key]
    assert storage == "VALUE"


def test_file_storage_read_file(
    storage_file, file_storage_cls
):
    storage = file_storage_cls(storage_file)
    assert "content" in storage.data


def test_file_storage_missing_raises(file_storage_cls):
    with pytest.raises(FileNotFoundError):
        file_storage_cls(Path("test"))


def test_file_storage_missing_ok(file_storage_cls):
    file_storage_cls.missing_ok = True
    storage = file_storage_cls(Path("test"))
    assert storage.data == {}


@pytest.fixture
def file_storage_cls(storage_file):
    class FileStorage(BaseFileStorageMixin):
        def __init__(self, file: Path, **kwargs):
            self.file = file
            super().__init__(**kwargs)

        def load_file_content(self, handler: IO) -> None:
            self.data.update({"content": handler.read()})

    return FileStorage


@pytest.fixture
def storage_file(tmp_path):
    file = tmp_path / "test"
    open(file, "w").close()
    yield file


def test_plain_structure_ignores_no_prefix(parser):
    parser.save_key_value("some_key", "value")
    assert parser.data == {}

    parser.save_key_value("APP_key", "value")
    assert parser.data["key"] == "value"


def test_second_level_key(parser):
    parser.save_key_value("APP_KEY1_KEY2", "value")
    assert parser.data["key1"] == {"key2": "value"}


def test_second_level_extends(parser):
    parser.save_key_value("APP_KEY1_KEY2", "value1")
    parser.save_key_value("APP_KEY1_KEY3", "value2")
    assert parser.data["key1"] == {
        "key2": "value1",
        "key3": "value2",
    }


@pytest.fixture
def parser():
    parser = PlainStructureParserMixin()
    parser.data = {}
    return parser
