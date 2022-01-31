import pytest

from src.config import EnvConfigStorage


@pytest.fixture
def storage():
    return EnvConfigStorage()


def test_env_config_outer(monkeypatch):
    monkeypatch.setenv("APP_KEY", "VALUE")
    storage = EnvConfigStorage()
    assert storage["key"] == "VALUE"


def test_key_filtering(storage):
    c = storage.app_keys("APP_")
    assert c("APP_KEY")


def test_second_level_variable(monkeypatch):
    monkeypatch.setenv("APP_KEY1_KEY2", "VALUE2")
    storage = EnvConfigStorage()
    assert storage["key1"]["key2"] == "VALUE2"


def test_multiple_third_level(monkeypatch):
    monkeypatch.setenv("APP_A_B_KEY1", "VALUE1")
    monkeypatch.setenv("APP_A_B_KEY2", "VALUE2")
    storage = EnvConfigStorage()
    assert storage["a"]["b"]["key1"] == "VALUE1"
    assert storage["a"]["b"]["key2"] == "VALUE2"


@pytest.mark.parametrize(
    "key,levels",
    [("APP_A_", ["a"]), ("APP_A__B", ["a", "b"])]
)
def test_empty_values_skipped(key, levels, monkeypatch):
    monkeypatch.setenv(key, "VALUE")
    storage = EnvConfigStorage()
    for key in levels:
        storage = storage[key]
    assert storage == "VALUE"
