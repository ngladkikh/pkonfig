import pytest

from pkonfig import DictStorage, Int, Config, ConfigTypeError, ConfigValueNotFoundError, Str


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
    with pytest.raises(ConfigValueNotFoundError):
        AppConfig(
            DictStorage(
                foo=0,
                inner_1={},
                inner_2={"required": 4321, "fiz": 321},
            )
        )


def test_root_level_attributes(config):
    assert config.foo == 0


def test_value_from_second_level_attribute(config: AppConfig):
    assert config.inner_1.required == 1234
    assert config.inner_2.required == 4321


def test_default_value_used_when_not_set(config):
    assert app_config.db1.port == 5432


def test_attr_validates_on_change(app_config):
    app_config.env = "test"
    assert app_config.env == "test"

    with pytest.raises(ConfigTypeError):
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

    with pytest.raises(ConfigValueNotFoundError):
        TConfig({})


def test_default_value_validated():
    class TConfig(Config):
        attr: int = "a"

    with pytest.raises(ConfigTypeError):
        TConfig({})


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


def test_not_annotated_default():
    class TestConfig(Config):
        s = "some value"

    config = TestConfig({})
    assert config.s == "some value"


def test_not_annotated_validates_on_change():
    class TestConfig(Config):
        s = 1

    with pytest.raises(ConfigTypeError):
        config = TestConfig({"s": "a"})
        assert config.s != "a"

    with pytest.raises(ConfigTypeError):
        config = TestConfig({"s": 1})
        config.s = "a"


def test_annotation_used_for_validation():
    class TestConfig(Config):
        attr: int

    with pytest.raises(ConfigTypeError):
        config = TestConfig({"attr": "a"})
        assert config.attr != "a"

    with pytest.raises(ConfigTypeError):
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
