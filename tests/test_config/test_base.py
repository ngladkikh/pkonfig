from typing import get_type_hints

import pytest

from pkonfig.base import (
    MetaConfig,
    NOT_SET, RETURN_TYPE,
    TypedParameter,
    extend_annotations,
    is_user_attr, replace
)
from pkonfig.fields import IntParam


def test_is_user_attr():
    class Test:
        f: int = 1
        _f = 0

        def m(self):
            pass

        def _m(self):
            pass

    t = Test()
    assert is_user_attr("f", t)
    assert not is_user_attr("_f", t)
    assert not is_user_attr("m", t)
    assert not is_user_attr("_m", t)
    assert not is_user_attr("__annotations__", t)


@pytest.fixture
def config_cls():
    class TestConfig(metaclass=MetaConfig):
        first: int
        second = 0.1
        third: bytes = b'test'
    return TestConfig


def test_annotations(config_cls):
    hints = get_type_hints(config_cls)
    assert "first" in hints
    assert "second" in hints
    assert "third" in hints


@pytest.fixture
def attributes(descriptor):
    return {
        "int": 1,
        "descriptor": descriptor(2)
    }


@pytest.fixture
def descriptor():
    class MyDescriptor(TypedParameter):
        def cast(self, string_value: str) -> RETURN_TYPE:
            return int(string_value)

        @property
        def returns(self):
            return int

    return MyDescriptor


def test_extend_annotations(attributes):
    extend_annotations(attributes)
    assert "__annotations__" in attributes
    assert attributes["__annotations__"]["int"] is int
    assert attributes["__annotations__"]["descriptor"] is int


def test_replace_class():
    class T:
        pass

    assert not replace(T)


def test_replace_not_set():
    assert replace(NOT_SET)


def test_replace_descriptor():
    assert not replace(IntParam())
