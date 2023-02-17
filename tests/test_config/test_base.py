from typing import Any, get_type_hints

import pytest

from pkonfig.base import (
    BaseConfig,
    NOT_SET,
    TypeMapper,
    Field,
    MetaConfig,
    Storage,
)
from pkonfig.fields import Int


@pytest.fixture
def config_cls():
    class TestConfig(BaseConfig):
        first: int
        second = 0.1
        third: bytes = b'test'
    return TestConfig


def test_user_attribute_filter():
    class TestConfig(BaseConfig):
        _f = 0.2
        f = 0.2

        def m(self):
            pass

        class Inner:
            pass

    t = TestConfig()
    assert t.is_user_attr("f")
    assert not t.is_user_attr("_f")
    assert not t.is_user_attr("m")
    assert not t.is_user_attr("Inner")


def test_annotations(config_cls):
    hints = get_type_hints(config_cls)
    assert "first" in hints
    assert "second" in hints
    assert "third" in hints


@pytest.fixture
def attributes(descriptor, any_type_descriptor):
    return {
        "int": 1,
        "descriptor": descriptor(2),
        "any_type_descriptor": any_type_descriptor(0.1)
    }


@pytest.fixture
def descriptor():
    class MyDescriptor(Field):
        def cast(self, value: str) -> int:
            return int(value)

    return MyDescriptor


@pytest.fixture
def any_type_descriptor():
    class AnyDescriptor(Field):
        def cast(self, value: str):
            return value

    return AnyDescriptor


@pytest.fixture
def config_with_descriptor(any_type_descriptor):
    class Config(BaseConfig):
        attr = any_type_descriptor()

        def __init__(self, **kwargs):
            super().__init__(kwargs)

    return Config


def test_attr_changed(config_with_descriptor):
    config = config_with_descriptor(attr=4)
    assert config.attr == 4

    config.attr = 5
    assert config.attr == 5


def test_no_value_raised(config_with_descriptor):
    config = config_with_descriptor()
    with pytest.raises(KeyError):
        assert config.attr


def test_attribute_uses_alias(any_type_descriptor):
    class Config(BaseConfig):
        attr = any_type_descriptor(alias="attr_alias")

        def __init__(self, **kwargs):
            super().__init__(kwargs)

    config = Config(attr_alias=1)
    assert config.attr == 1


def test_no_value_default_used(any_type_descriptor):
    class Config(BaseConfig):
        attr = any_type_descriptor(1)

        def __init__(self, **kwargs):
            super().__init__(kwargs)

    config = Config()
    assert config.attr == 1


def test_default_value_validated(descriptor):
    class Config(BaseConfig):
        attr = descriptor("a")

        def __init__(self, **kwargs):
            super().__init__(kwargs)

    config = Config()
    with pytest.raises(ValueError):
        assert config.attr


def test_none_omits_cast(descriptor):
    class Config(BaseConfig):
        attr = descriptor(None)

    config = Config({})
    assert config.attr is None


def test_nullable_field(descriptor):
    class Config(BaseConfig):
        attr = descriptor(nullable=True)

    config = Config({"attr": None})
    assert config.attr is None


def test_non_nullable_field_raises(descriptor):
    class Config(BaseConfig):
        attr = descriptor()

    with pytest.raises(TypeError):
        c = Config({"attr": None})
        assert c.attr


def test_extend_annotations(attributes):
    MetaConfig.extend_annotations(attributes)
    assert "__annotations__" in attributes
    assert attributes["__annotations__"]["int"] is int
    assert attributes["__annotations__"]["descriptor"] is int
    assert attributes["__annotations__"]["any_type_descriptor"] is Any


def test_replace_class():
    class T:
        pass

    assert not TypeMapper.replace(T)


def test_replace_not_set():
    assert TypeMapper.replace(NOT_SET)


def test_replace_descriptor():
    assert not TypeMapper.replace(Int())


def test_config_alias_is_replaced(config_cls):
    c = config_cls()
    assert c._alias is None

    c.__set_name__(config_cls, "new_awesome_name")
    assert c._alias == "new_awesome_name"
    cget = c.__get__(config_cls())
    assert cget._root_path == "new_awesome_name__"
    assert c._root_path == "new_awesome_name__"


def test_storage_uppers_all_keys():
    s = Storage({"a": 1, "BB": 2}, prefix="")
    assert s["A"] == 1
    assert s["BB"] == 2
    assert s["a"] == 1
    assert s["bb"] == 2
    assert s["bB"] == 2
    assert s["Bb"] == 2
