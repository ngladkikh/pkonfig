import pytest

from pkonfig import (
    Config,
    ConfigTypeError,
    ConfigValueNotFoundError,
    DictStorage,
    Int,
    Str,
)


@pytest.fixture
def inner_cls():
    class Inner(Config):
        foo = Str("baz", nullable=False)
        fiz = Int(123, nullable=False)
        required = Int()

    return Inner


@pytest.fixture
def app_config_cls(inner_cls):
    class AppConfig(Config):
        inner_1 = inner_cls()
        inner_2: inner_cls
        foo = Int()

    return AppConfig


@pytest.fixture
def storage():
    return DictStorage(
        foo=0,
        inner_1={"required": 1234, "foo": "biz"},
        inner_2={"required": 4321, "fiz": 321},
    )


@pytest.fixture
def config(storage, app_config_cls):
    return app_config_cls(storage)


def test_app_config_fails_on_root_level_attr_missing(app_config_cls):
    with pytest.raises(ConfigValueNotFoundError):
        app_config_cls(
            DictStorage(
                inner_1={"required": 1234, "foo": "biz"},
                inner_2={"required": 4321, "fiz": 321},
            )
        )


def test_app_config_fails_on_inner_level_attr_missing():

    class FooConfig(Config):
        foo: int

    class BarConfig(Config):
        foo = FooConfig()

    with pytest.raises(ConfigValueNotFoundError):
        BarConfig(DictStorage(foo={}))


def test_app_config_fails_on_inner_defined_with_type_level_attr_missing():

    class FooConfig(Config):
        foo: int

    class BarConfig(Config):
        foo: FooConfig

    with pytest.raises(ConfigValueNotFoundError):
        BarConfig(DictStorage(foo={}))


def test_root_level_attributes(config):
    assert config.foo == 0


def test_value_from_second_level_attribute(config):
    assert config.inner_1.required == 1234
    assert config.inner_2.required == 4321


def test_default_value_used_when_not_set(app_config_cls):
    config = app_config_cls(
        DictStorage(
            foo=0,
            inner_1={"required": 1234, "foo": "biz"},
            inner_2={"required": 4321},
        )
    )
    # Value taken from config
    assert config.inner_1.foo == "biz"
    # Default value is used
    assert config.inner_2.foo == "baz"


def test_inheritance():
    class Parent(Config):
        s = Str()

    class Child(Parent):
        i = Int()

    config = Child(DictStorage(s="some", i=1))
    assert config.i == 1
    assert config.s == "some"


def test_field_type_is_not_recreated():
    """Test instantiated attributes are not recreated."""

    class C(Config):
        s: str = Str(default="foo")

    config = C()
    assert config.s == "foo"


def test_unknown_types_fail():

    class CustomType:
        pass

    with pytest.raises(ConfigTypeError):

        class Foo(Config):
            foo: CustomType


def test_default_typed_value():
    class C(Config):
        i: int = 1

    assert C().i == 1


def test_pkonfig_type_annotation():
    class C(Config):
        foo: Str = "foo"

    assert C().foo == "foo"
