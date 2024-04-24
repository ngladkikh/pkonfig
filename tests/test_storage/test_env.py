from pkonfig.storage import Env


def test_env_config_outer(monkeypatch):
    monkeypatch.setenv("APP_KEY", "VALUE")
    storage = Env(delimiter="_")
    assert storage[("key",)] == "VALUE"


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
