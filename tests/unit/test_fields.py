from enum import Enum
from pathlib import Path

import pytest

from pkonfig import (
    Bool,
    Choice,
    Config,
    ConfigTypeError,
    ConfigValueNotFoundError,
    DictStorage,
    EnumField,
    File,
    Float,
    Folder,
    Int,
    ListField,
    LogLevel,
    PathField,
    Str,
)


@pytest.fixture
def config_factory():
    def config_mock(**storage) -> Config:
        storage = DictStorage(**storage)
        config = Config(storage)
        return config

    return config_mock


def test_not_nullable_raises_exception_on_null(config_factory):
    config = config_factory(attr=None)
    with pytest.raises(ConfigTypeError):
        Str(nullable=False, alias="attr").get(config)


def test_value_not_found_raises_exception(config_factory):
    config = config_factory()
    with pytest.raises(ConfigValueNotFoundError):
        Str(alias="attr").get(config)


def test_int_param(config_factory):
    int_config = config_factory(attr=3)
    assert (
        Int(alias="attr").get(
            int_config,
        )
        == 3
    )


def test_casts_on_set(config_factory):
    int_config = config_factory(attr=3)
    attribute = Int()
    with pytest.raises(ConfigTypeError):
        attribute.__set__(int_config, "a")


def test_validates_value_on_set(config_factory):
    config = config_factory(attr=10)
    attr = Choice([10, 20, 30], alias="attr")
    assert attr.get(config) == 10
    attr.__set__(config, 20)
    assert attr.get(config) == 20
    with pytest.raises(ConfigTypeError):
        attr.__set__(config, 40)


def test_default_value_is_validated(config_factory):
    config = config_factory(attr=10)
    with pytest.raises(ConfigTypeError):
        Int(default="a").get(config)


def test_none_is_not_casted(config_factory):
    assert Int(None, alias="attr").get(config_factory()) is None
    assert Int(alias="attr", nullable=True).get(config_factory(attr=None)) is None


def test_only_int_accepted(config_factory):
    int_config = config_factory(attr="a")
    with pytest.raises(ConfigTypeError):
        Int(alias="attr").get(int_config)


def test_float_only_accepted(config_factory):
    float_config = config_factory(attr="a")
    with pytest.raises(ConfigTypeError):
        Float(alias="attr").get(float_config)


def test_float(config_factory):
    float_config = config_factory(attr="0.33")
    assert Float(alias="attr").get(float_config) == 0.33


def test_string_param_casts(config_factory):
    config = config_factory(attr=2)
    assert Str(alias="attr").get(config) == "2"


def test_path_cast(config_factory):
    config = config_factory(attr="/some")
    assert PathField(missing_ok=True, alias="attr").get(config) == Path("/some")


def test_path_not_exists_raises(config_factory):
    config = config_factory(attr="/some")
    with pytest.raises(ConfigTypeError):
        PathField(alias="attr").get(config)


def test_path_existence_checked(tmp_path, config_factory):
    existing_file = tmp_path / "test"
    config = config_factory(attr=existing_file)
    with open(existing_file, "w"):
        PathField(alias="attr").get(config)


def test_file_raises_error_if_folder(tmp_path, config_factory):
    config = config_factory(attr=tmp_path)
    with pytest.raises(ConfigTypeError):
        File(alias="attr").get(config)


def test_file_field_respects_missing_ok(config_factory):
    config = config_factory(attr="not_exist")
    assert File(missing_ok=True, alias="attr").get(config) == Path("not_exist")


def test_is_dir_raises_exception_on_file(tmp_path, config_factory):
    existing_file = tmp_path / "test"
    config = config_factory(attr=existing_file)
    with open(existing_file, "w"):
        with pytest.raises(ConfigTypeError):
            Folder(alias="attr").get(config)


@pytest.fixture
def enum_attr_config():
    class Color(Enum):
        red = 1
        green = 2
        blue = 3

    return Color


def test_enum_param_returns_value(enum_attr_config, config_factory):
    config = config_factory(attr="red")
    assert EnumField(enum_attr_config, alias="attr").get(config) is enum_attr_config.red


def test_enum_raises_error(enum_attr_config, config_factory):
    config = config_factory(attr="foo")
    with pytest.raises(ConfigTypeError):
        EnumField(enum_attr_config, alias="attr").get(config)


def test_choice_raises_error(config_factory):
    config = config_factory(attr="foo")
    with pytest.raises(ConfigTypeError):
        Choice(["fiz", "baz"], alias="attr").get(config)


def test_choice(config_factory):
    config = config_factory(attr="foo")
    assert Choice(["foo", "baz"], alias="attr").get(config) == "foo"


def test_choice_casts_values(config_factory):
    config = config_factory(attr="10")
    assert Choice([0, 10], cast_function=int, alias="attr").get(config) == 10


@pytest.mark.parametrize(
    "level,value", [("info", 20), ("INFO", 20), ("Error", 40), ("WaRnInG", 30)]
)
def test_log_level_case_insensitive(level, value, config_factory):
    config = config_factory(attr=level)
    assert LogLevel(alias="attr").get(config) == value


@pytest.mark.parametrize("value", ["true", "TRUE", "+", 1, "1", True, "yes", "Y", "y"])
def test_truthy_bool(value, config_factory):
    config = config_factory(attr=value)
    assert Bool(alias="attr").get(config)


def test_cache_used():
    class TConf(Config):
        attr = Int()

    config = TConf(DictStorage(attr=1))
    assert config.attr == 1

    config._storage = DictStorage(attr=2)
    assert config.attr == 1


@pytest.mark.parametrize(
    "raw_value",
    ("1, 2, 3", [1, 2, 3], [1, "2", 3], "1,2,3")
)
def test_list_fields_cast(raw_value, config_factory):
    field = ListField(alias="attr", cast_function=int)

    config = config_factory(attr=raw_value)
    assert field.get(config) == [1, 2, 3]
