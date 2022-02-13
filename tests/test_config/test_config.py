import pytest

from pkonfig.config import EmbeddedConfig, OuterMostConfig
from pkonfig.fields import IntParam, StrParam


def test_outer_config():
    class TestConfig(OuterMostConfig):
        s: str
        i: int = 1

    storage = dict(s="some", i="12")
    config = TestConfig(storage)
    assert config.s == "some"
    assert config.i == 12


def test_raises_key_error():
    class TestConfig(OuterMostConfig):
        s: str

    with pytest.raises(KeyError):
        TestConfig({})


def test_raises_value_error():
    class TestConfig(OuterMostConfig):
        s: int

    storage = dict(s='a')
    with pytest.raises(ValueError):
        TestConfig(storage)


def test_inner_config():
    class Inner(EmbeddedConfig):
        f: float

    class TestConfig(OuterMostConfig):
        inner = Inner()
    storage = dict(inner={"f": 0.1})
    config = TestConfig(storage)
    assert config.inner.f == 0.1


def test_not_annotated_default():
    class TestConfig(OuterMostConfig):
        s = "some value"
    config = TestConfig({})
    assert config.s == "some value"


def test_not_annotated():
    class TestConfig(OuterMostConfig):
        i: int = 1
        s = "some value"
    storage = dict(s="new")
    config = TestConfig(storage)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor():
    class TestConfig(OuterMostConfig):
        s = StrParam("test")
        i = IntParam(1)
    storage = dict(s="new")
    config = TestConfig(storage)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor_no_default():
    class TestConfig(OuterMostConfig):
        s = StrParam()
    storage = dict()
    with pytest.raises(KeyError):
        TestConfig(storage)


def test_methods_ignored():
    class TestConfig(OuterMostConfig):
        i = 1

        def m(self):
            return 10

    config = TestConfig({"m": 1})
    assert config.i == 1
    assert callable(config.m)
