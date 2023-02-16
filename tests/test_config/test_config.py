from decimal import Decimal
from typing import Any, Type, get_type_hints

import pytest

from pkonfig.base import Field, NOT_SET, TypeMapper
from pkonfig.config import Config, DefaultMapper
from pkonfig.fields import DecimalField, Int, Str


@pytest.fixture
def config4test():
    class TestConfig(Config):
        def __init__(self, storage):
            super().__init__(storage=storage, alias=None)
    return TestConfig


def test_outer_config(config4test):
    class TestConfig(config4test):
        s: str
        i = 1

    storage = dict(S="some", I="12")
    config = TestConfig(storage)
    assert config.s == "some"
    assert config.i == 12


def test_raises_key_error(config4test):
    class TestConfig(config4test):
        s: str

    with pytest.raises(KeyError):
        c = TestConfig({})
        assert c.s


def test_raises_value_error(config4test):
    class TestConfig(config4test):
        s: int

    storage = dict(S='a')
    with pytest.raises(ValueError):
        assert TestConfig(storage).s


def test_inner_config(config4test):
    class Inner(Config):
        f: float

    class TestConfig(config4test):
        inner = Inner()

    storage = {"INNER__F": 0.1}
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
    storage = dict(S="new")
    config = TestConfig(storage, alias=None)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor():
    class TestConfig(Config):
        s = Str("test")
        i = Int(1)
    storage = dict(S="new")
    config = TestConfig(storage, alias=None)
    assert config.s == "new"
    assert config.i == 1


def test_descriptor_no_default():
    class TestConfig(Config):
        s = Str()
    storage = dict()
    with pytest.raises(KeyError):
        assert TestConfig(storage).s


def test_methods_ignored():
    class TestConfig(Config):
        i = 1

        def m(self):
            return 10

    config = TestConfig({"m": 1})
    assert config.i == 1
    assert callable(config.m)
    assert config.m() == 10


def test_fail_fast():
    class TestConfig(Config):
        i: int

    with pytest.raises(KeyError):
        assert TestConfig({}).i


def test_three_level():
    class InnerMost(Config):
        s: str

    class Inner(Config):
        f: float
        i = InnerMost()

    class TestConfig(Config):
        inner = Inner()

    storage = dict(inner={"f": 0.1, "i": {"s": "text"}})
    config = TestConfig(storage, alias=None)
    assert config.inner.f == 0.1
    assert config.inner.i.s == "text"


def test_inheritance():
    class Parent(Config):
        s: str

    class Child(Parent):
        i: int

    config = Child(dict(s="some", i=1))
    assert config.s == "some"
    assert config.i == 1


def test_default_mapper_ignores_unknown_types():
    class Custom:
        pass

    mapper = DefaultMapper()

    value = Custom()
    descriptor = mapper.descriptor(Custom, value)
    assert descriptor is value


def test_strict_mapper(strict_int_mapper):

    class AppConfig(Config):
        _mapper = strict_int_mapper()

        attr = Int()

    config = AppConfig(dict(attr=1))
    assert config.attr == 1


def test_strict_mapper_raises_error(strict_int_mapper):
    with pytest.raises(KeyError):
        class AppConfig(Config):
            _mapper = strict_int_mapper()

            attr: float


@pytest.fixture
def strict_int_mapper():
    class StrictMapper(TypeMapper):
        map = {
            int: Int
        }

        def descriptor(self, type_: Type, value: Any = NOT_SET) -> Field:
            return self.map[type_](value)
    return StrictMapper


def test_change_type_mapping_on_init():
    class AppConfig(Config):
        _mapper = DefaultMapper({float: DecimalField})
        attr: float

    config = AppConfig(dict(attr=0.3))
    assert isinstance(config.attr, Decimal)


def test_embedded_config_type_remains():
    class Inner(Config):
        f: float

    class TestConfig(Config):
        inner = Inner()

    storage = dict(inner={"f": 0.1, "i": {"s": "text"}})
    config = TestConfig(storage)
    assert get_type_hints(config)["inner"] is Inner
    assert isinstance(config.inner, Inner)


def test_inner_uses_alias():
    class Inner(Config):
        f: float

    class TestConfig(Config):
        inner = Inner(alias="foo")

    storage = dict(foo={"f": 0.1, "i": {"s": "text"}})
    config = TestConfig(storage)
    assert config.inner.f == 0.1


def test_inner_config_respects_defaults():
    class Inner(Config):
        attr = 1

    class AppConfig(Config):
        inner = Inner()

    config = AppConfig({})
    assert config.inner.attr == 1


def test_inner_config_raises_exception():
    class Inner(Config):
        attr: int

    class AppConfig(Config):
        inner = Inner()

    with pytest.raises(KeyError):
        assert AppConfig({}).inner.attr
