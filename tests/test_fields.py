from enum import Enum
from typing import Type
from uuid import uuid4

import pytest

from pkonfig import Storage
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


def build_config(descriptor) -> Type["TestConfig"]:
    class TestConfig(Config):
        attr = descriptor

        def __init__(self, **kwargs):
            super().__init__(kwargs, alias="")

    return TestConfig


@pytest.fixture
def int_config():
    cls = build_config(Int())
    return cls(attr=3)


def test_int_param(int_config):
    assert int_config.attr == 3


def test_only_int_accepted(int_config):
    with pytest.raises(ValueError):
        int_config.attr = "a"


@pytest.fixture
def float_config():
    cls = build_config(Float())
    return cls(attr=0.3)


def test_float_only_accepted(float_config):
    with pytest.raises(ValueError):
        float_config.attr = "a"


def test_string_param_casts():
    cls = build_config(Str())
    config = cls(attr=2)
    assert config.attr == "2"


def test_path_cast():
    cls = build_config(PathField(missing_ok=True))
    config = cls(attr="/some")
    assert config.attr.name == "some"


def test_path_not_exists_raises():
    cls = build_config(PathField())
    with pytest.raises(FileNotFoundError):
        assert cls(attr="/some").attr


def test_is_file_checked(tmp_path):
    cls = build_config(File())
    existing_file = tmp_path / "test"
    with open(existing_file, "w"):
        config = cls(attr=existing_file)
        assert config.attr.name == "test"

    with pytest.raises(TypeError):
        config.attr = tmp_path


def test_file_field_respects_missing_ok():
    cls = build_config(File(missing_ok=True))
    config = cls(attr="not_exists")
    assert not config.attr.exists()


def test_folder_field_respects_missing_ok():
    cls = build_config(Folder(missing_ok=True))
    config = cls(attr="not_exists")
    assert not config.attr.exists()


def test_is_dir_checked(tmp_path):
    cls = build_config(Folder())
    config = cls(attr=tmp_path)
    existing_file = tmp_path / "test"
    with open(existing_file, "w"):
        with pytest.raises(TypeError):
            config.attr = existing_file


@pytest.fixture
def enum_attr_config():
    class Color(Enum):
        red = 1
        green = 2
        blue = 3

    return build_config(EnumField(Color)), Color


def test_enum_param_returns_value(enum_attr_config):
    cls, enum_cls = enum_attr_config
    config = cls(attr="red")
    assert config.attr is enum_cls.red


def test_enum_raises_error(enum_attr_config):
    enum_attr_config, _ = enum_attr_config
    with pytest.raises(KeyError):
        assert enum_attr_config(attr="foo").attr


def test_choice_raises_error():
    cls = build_config(Choice(["foo", "bar"]))
    with pytest.raises(TypeError):
        assert cls(attr="test").attr


def test_choice():
    cls = build_config(Choice(["foo", "bar"]))
    config = cls(attr="foo")
    assert config.attr == "foo"


def test_choice_casts_values():
    cls = build_config(Choice([10, 100], int))
    config = cls(attr="10")
    assert config.attr == 10


@pytest.mark.parametrize(
    "level,value", [("info", 20), ("INFO", 20), ("Error", 40), ("WaRnInG", 30)]
)
def test_log_level_case_insensitive(level, value):
    cls = build_config(LogLevel())
    config = cls(attr=level)
    assert config.attr == value


@pytest.mark.parametrize("value", ["false", "FALSE", "some", "", str(uuid4())])
def test_falsy_debug(value):
    cls = build_config(DebugFlag())
    config = cls(attr=value)
    assert not config.attr


def test_truthy_debug():
    cls = build_config(DebugFlag())
    config = cls(attr="true")
    assert config.attr


def test_no_cache_used():
    class TConf(Config):
        attr = Int(no_cache=True)

    config = TConf(Storage({"attr": 1}))
    assert config.attr == 1

    config._storage = Storage({"attr": 2})
    assert config.attr == 2


def test_cache_used():
    class TConf(Config):
        attr = Int(no_cache=False)

    config = TConf(Storage({"attr": 1}))
    assert config.attr == 1

    config._storage = Storage({"attr": 2})
    assert config.attr == 1
