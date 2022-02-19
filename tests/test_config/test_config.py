import pytest

from pkonfig.config import Config, EmbeddedConfig
from pkonfig.fields import IntParam, StrParam


def test_outer_config():
    class TestConfig(Config):
        s: str
        i = 1

    storage = dict(s="some", i="12")
    config = TestConfig(storage)
    assert config.s == "some"
    assert config.i == 12


def test_raises_key_error():
    class TestConfig(Config):
        s: str

    with pytest.raises(KeyError):
        TestConfig({})


def test_raises_value_error():
    class TestConfig(Config):
        s: int

    storage = dict(s='a')
    with pytest.raises(ValueError):
        TestConfig(storage)


def test_inner_config():
    class Inner(EmbeddedConfig):
        f: float

    class TestConfig(Config):
        inner = Inner()

    storage = dict(inner={"f": 0.1})
    config = TestConfig(storage)
    assert config.inner.f == 0.1


def test_not_annotated_default():
    class TestConfig(Config):
        s = "some value"
    config = TestConfig({})
    assert config.s == "some value"


def test_not_annotated():
    class TestConfig(Config):
        i: int = 1
        s = "some value"
    storage = dict(s="new")
    config = TestConfig(storage)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor():
    class TestConfig(Config):
        s = StrParam("test")
        i = IntParam(1)
    storage = dict(s="new")
    config = TestConfig(storage)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor_no_default():
    class TestConfig(Config):
        s = StrParam()
    storage = dict()
    with pytest.raises(KeyError):
        TestConfig(storage)


def test_methods_ignored():
    class TestConfig(Config):
        i = 1

        def m(self):
            return 10

    config = TestConfig({"m": 1})
    assert config.i == 1
    assert callable(config.m)
    assert config.m() == 10


def test_dynamic_config():
    class TestConfig(Config):
        i = IntParam(no_cache=True)
    storage = {"i": "2"}
    config = TestConfig(storage)
    assert config.i == 2

    storage["i"] = "3"
    assert config.i == 3


def test_fail_fast():
    class TestConfig(Config):
        i: int

    with pytest.raises(KeyError):
        TestConfig({})


def test_three_level():
    class InnerMost(EmbeddedConfig):
        s: str

    class Inner(EmbeddedConfig):
        f: float
        i = InnerMost()

    class TestConfig(Config):
        inner = Inner()

    storage = dict(inner={"f": 0.1, "i": {"s": "text"}})
    config = TestConfig(storage)
    assert config.inner.f == 0.1
    assert config.inner.i.s == "text"
