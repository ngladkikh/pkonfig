from enum import Enum
from pathlib import Path
from typing import Any, Callable, Type
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from pkonfig import DictStorage
from pkonfig.base import ConfigTypeError
from pkonfig.config import Config
from pkonfig.fields import (
    Choice,
    DebugFlag,
    EnumField,
    File,
    Float,
    Folder,
    Int,
    LogLevel,
    PathField,
    Str,
)


@pytest.fixture
def config_factory():
    def config_mock(**storage) -> Config:
        config = MagicMock(spec=Config)
        storage = DictStorage(**storage)
        config.get_storage = MagicMock(return_value=storage)
        return config

    return config_mock


def test_int_param(config_factory):
    int_config = config_factory(attr=3)
    assert Int(alias="attr").get_from_storage(int_config) == 3


def test_only_int_accepted(config_factory):
    int_config = config_factory(attr="a")
    with pytest.raises(ConfigTypeError):
        Int(alias="attr").get_from_storage(int_config)


def test_float_only_accepted(config_factory):
    float_config = config_factory(attr="a")
    with pytest.raises(ConfigTypeError):
        Float(alias="attr").get_from_storage(float_config)


def test_float(config_factory):
    float_config = config_factory(attr="0.33")
    assert Float(alias="attr").get_from_storage(float_config) == 0.33


def test_string_param_casts(config_factory):
    config = config_factory(attr=2)
    assert Str(alias="attr").get_from_storage(config) == "2"


def test_path_cast(config_factory):
    config = config_factory(attr="/some")
    assert PathField(missing_ok=True, alias="attr").get_from_storage(config) == Path("/some")


def test_path_not_exists_raises(config_factory):
    config = config_factory(attr="/some")
    with pytest.raises(FileNotFoundError):
        PathField(alias="attr").get_from_storage(config)


def test_path_existence_checked(tmp_path, config_factory):
    existing_file = tmp_path / "test"
    config = config_factory(attr=existing_file)
    with open(existing_file, "w"):
        PathField(alias="attr").get_from_storage(config)


def test_file_raises_error_if_folder(tmp_path, config_factory):
    config = config_factory(attr=tmp_path)
    with pytest.raises(ConfigTypeError):
        File(alias="attr").get_from_storage(config)


def test_file_field_respects_missing_ok(config_factory):
    config = config_factory(attr="not_exist")
    assert File(alias="attr", missing_ok=True).get_from_storage(config) == Path("not_exist")


def test_is_dir_raises_exception_on_file(tmp_path, config_factory):
    existing_file = tmp_path / "test"
    config = config_factory(attr=existing_file)
    with open(existing_file, "w"):
        with pytest.raises(ConfigTypeError):
            Folder(alias="attr").get_from_storage(config)


@pytest.fixture
def enum_attr_config():
    class Color(Enum):
        red = 1
        green = 2
        blue = 3

    return Color


def test_enum_param_returns_value(enum_attr_config, config_factory):
    config = config_factory(attr="red")
    assert EnumField(enum_attr_config, alias="attr").get_from_storage(config) is enum_attr_config.red


def test_enum_raises_error(enum_attr_config, config_factory):
    config = config_factory(attr="foo")
    with pytest.raises(KeyError):
        EnumField(enum_attr_config, alias="attr").get_from_storage(config)


def test_choice_raises_error(config_factory):
    config = config_factory(attr="foo")
    with pytest.raises(ConfigTypeError):
        Choice(["fiz", "baz"], alias="attr").get_from_storage(config)


def test_choice(config_factory):
    config = config_factory(attr="foo")
    assert Choice(["foo", "baz"], alias="attr").get_from_storage(config) == "foo"


def test_choice_casts_values(config_factory):
    config = config_factory(attr="10")
    assert Choice([0, 10], cast_function=int, alias="attr").get_from_storage(config) == 10


@pytest.mark.parametrize(
    "level,value", [("info", 20), ("INFO", 20), ("Error", 40), ("WaRnInG", 30)]
)
def test_log_level_case_insensitive(level, value, config_factory):
    config = config_factory(attr=level)
    assert LogLevel(alias="attr").get_from_storage(config) == value


@pytest.mark.parametrize("value", ["true", "TRUE", "+", 1, "1", True, "yes", "Y", "y"])
def test_truthy_debug(value, config_factory):
    config = config_factory(attr=value)
    assert DebugFlag(alias="attr").get_from_storage(config)


def test_cache_used():
    class TConf(Config):
        attr = Int(no_cache=False)

    config = TConf(DictStorage(attr=1))
    assert config.attr == 1

    config._storage = DictStorage(attr=2)
    assert config.attr == 1
