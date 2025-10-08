import pytest

from pkonfig import Config, ConfigValueNotFoundError, DictStorage, Int, Str


class Inner(Config):
    foo = Str("baz", nullable=False)
    fiz = Int(123, nullable=False)
    required = Int()


class AppConfig(Config):
    inner_1: Inner = Inner()
    inner_2 = Inner()
    foo = Int()


@pytest.fixture
def storage():
    return DictStorage(
        foo=0,
        inner_1={"required": 1234, "foo": "biz"},
        inner_2={"required": 4321, "fiz": 321},
    )


@pytest.fixture
def config(storage):
    return AppConfig(storage)


def test_app_config_fails_on_root_level_attr_missing():
    with pytest.raises(ConfigValueNotFoundError):
        AppConfig(
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


def test_value_from_second_level_attribute(config: AppConfig):
    assert config.inner_1.required == 1234
    assert config.inner_2.required == 4321


def test_default_value_used_when_not_set():
    config = AppConfig(DictStorage(
        foo=0,
        inner_1={"required": 1234, "foo": "biz"},
        inner_2={"required": 4321},
    ))
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
