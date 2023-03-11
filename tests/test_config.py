import tempfile
from pathlib import Path

import pytest

from pkonfig import Choice, Config, Env, Int, LogLevel
from pkonfig.storage import DotEnv


@pytest.fixture(scope="module")
def tmp_path():
    with tempfile.TemporaryDirectory() as dir:
        yield Path(dir)


@pytest.fixture(scope="module")
def dot_env_storage(tmp_path):
    file = tmp_path / ".env"
    with open(file, "w") as fh:
        lines = [
            "APP__LOG_LEVEL= debug",
            "APP__DB1__HOST=10.10.10.10",
            "APP__DB1__USER = user",
            "APP__DB1__PASSWORD = securedPass",
            "APP__ENV =local",
        ]
        fh.write("\n".join(lines))
    return DotEnv(file, delimiter="__")


@pytest.fixture
def env_storage(monkeypatch):
    monkeypatch.setenv("APP__LOG_LEVEL", "warning")
    monkeypatch.setenv("APP__DB2__HOST", "1.1.1.1")
    monkeypatch.setenv("APP__DB2__USER", "admin")
    monkeypatch.setenv("APP__DB2__PASSWORD", "secret")
    monkeypatch.setenv("APP__DB2__PORT", "54321")
    return Env(delimiter="__")


@pytest.fixture
def config_cls():
    class PG(Config):
        host = "localhost"
        port = 5432
        user = "postgres"
        password = "postgres"

    class AppConfig(Config):
        db1 = PG()
        db2 = PG()
        log_level = LogLevel("INFO")
        env = Choice(["local", "prod", "test"], default="prod")

    return AppConfig


@pytest.fixture
def app_config(config_cls, dot_env_storage, env_storage):
    config = config_cls(dot_env_storage, env_storage)
    return config


def test_first_storage_values_used_first(app_config):
    assert app_config.log_level == 10


def test_value_from_second_storage_taken_when_not_set_before(app_config):
    assert app_config.db2.user == "admin"
    assert app_config.db2.password == "secret"
    assert app_config.db2.port == 54321


def test_default_value_used_when_not_set(app_config):
    assert app_config.db1.port == 5432


def test_attr_validates_on_change(app_config):
    app_config.env = "test"
    assert app_config.env == "test"

    with pytest.raises(TypeError):
        app_config.env = "some"


def test_attribute_values_got_found_by_alias():
    class TestConf(Config):
        my_attr = Int(alias="myAttr")

    config = TestConf({"myAttr": 1})
    assert config.my_attr == 1


def test_multilevel_attribute_values_got_found_by_alias():
    class Inner(Config):
        attr: int

    class TestConf(Config):
        my_attr = Inner(alias="myAttr")
        inner = Inner()

    storage = {
        "myAttr": {"attr": 1},
        "inner": {"attr": 2},
    }
    config = TestConf(storage)
    assert config.my_attr.attr == 1
    assert config.inner.attr == 2


def test_multilevel_values_found_in_second_storage():
    class Inner(Config):
        attr: str

    class TestConf(Config):
        inner = Inner()

    storage_1 = {"inner": {}}
    storage_2 = {"inner": {"attr": "some"}}
    config = TestConf(storage_1, storage_2)
    assert config.inner.attr == "some"


def test_no_value_raised():
    class TConfig(Config):
        attr: int

    config = TConfig({})
    with pytest.raises(KeyError):
        assert config.attr


def test_default_value_validated():
    class TConfig(Config):
        attr: int = "a"

    config = TConfig({})
    with pytest.raises(ValueError):
        assert config.attr


def test_none_omits_cast():
    class TConfig(Config):
        attr = Int(None)

    config = TConfig({})
    assert config.attr is None


def test_nullable_field_allowed_to_be_null():
    class TConfig(Config):
        attr = Int(nullable=True)

    config = TConfig({"attr": None})
    assert config.attr is None


def test_non_nullable_field_raises_exception_on_null():
    class TConfig(Config):
        attr = Int()

    with pytest.raises(TypeError):
        c = TConfig({"attr": None})
        assert c.attr


def test_not_annotated_default():
    class TestConfig(Config):
        s = "some value"

    config = TestConfig({})
    assert config.s == "some value"


def test_not_annotated_validates_on_change():
    class TestConfig(Config):
        s = 1

    with pytest.raises(ValueError):
        config = TestConfig({"s": "a"})
        assert config.s != "a"

    with pytest.raises(ValueError):
        config = TestConfig({"s": 1})
        config.s = "a"


def test_annotation_used_for_validation():
    class TestConfig(Config):
        attr: int

    with pytest.raises(ValueError):
        config = TestConfig({"attr": "a"})
        assert config.attr != "a"

    with pytest.raises(ValueError):
        config = TestConfig({"attr": 1})
        config.attr = "a"


def test_inheritance():
    class Parent(Config):
        s: str

    class Child(Parent):
        i: int

    config = Child(dict(s="some", i=1))
    assert config.s == "some"
    assert config.i == 1
