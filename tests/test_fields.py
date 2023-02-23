from enum import Enum
from typing import Type
from uuid import uuid4

import pytest

from pkonfig.config import Config
from pkonfig.fields import (
    DebugFlag,
    Int,
    Float,
    Str,
    PathField,
    File,
    Folder,
    EnumField,
    LogLevel,
    Choice,
)


def build_config(descriptor) -> Type["Config"]:
    class TestConfig(Config):
        attr = descriptor

        def __init__(self, **kwargs):
            super().__init__(storage=kwargs, alias=None)

    return TestConfig


@pytest.fixture
def int_config():
    cls = build_config(Int())
    return cls(ATTR=3)


def test_int_param(int_config):
    assert int_config.attr == 3


def test_only_int_accepted(int_config):
    with pytest.raises(ValueError):
        int_config.attr = 'a'


@pytest.fixture
def float_config():
    cls = build_config(Float())
    return cls(attr=0.3)


def test_float_only_accepted(float_config):
    with pytest.raises(ValueError):
        float_config.attr = 'a'


def test_string_param_casts():
    cls = build_config(Str())
    config = cls(ATTR=2)
    assert config.attr == "2"


def test_path_cast():
    cls = build_config(PathField(missing_ok=True))
    config = cls(ATTR="/some")
    assert config.attr.name == "some"


def test_path_not_exists_raises():
    cls = build_config(PathField())
    with pytest.raises(FileNotFoundError):
        assert cls(ATTR="/some").attr


def test_is_file_checked(tmp_path):
    cls = build_config(File())
    existing_file = tmp_path / "test"
    with open(existing_file, "w"):
        config = cls(ATTR=existing_file)
        assert config.attr.name == "test"

    with pytest.raises(TypeError):
        config.attr = tmp_path


def test_file_field_respects_missing_ok():
    cls = build_config(File(missing_ok=True))
    config = cls(ATTR="not_exists")
    assert not config.attr.exists()


def test_folder_field_respects_missing_ok():
    cls = build_config(Folder(missing_ok=True))
    config = cls(ATTR="not_exists")
    assert not config.attr.exists()


def test_is_dir_checked(tmp_path):
    cls = build_config(Folder())
    config = cls(ATTR=tmp_path)
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
    config = cls(ATTR="red")
    assert config.attr is enum_cls.red


def test_enum_raises_error(enum_attr_config):
    enum_attr_config, _ = enum_attr_config
    with pytest.raises(KeyError):
        assert enum_attr_config(ATTR="foo").attr


def test_choice_raises_error():
    cls = build_config(Choice(["foo", "bar"]))
    with pytest.raises(TypeError):
        assert cls(ATTR="test").attr


def test_choice():
    cls = build_config(Choice(["foo", "bar"]))
    config = cls(ATTR="foo")
    assert config.attr == "foo"


def test_choice_casts_values():
    cls = build_config(
        Choice(
            [10, 100],
            int
        )
    )
    config = cls(ATTR="10")
    assert config.attr == 10


@pytest.mark.parametrize(
    "level,value",
    [
        ("info", 20),
        ("INFO", 20),
        ("Error", 40),
        ("WaRnInG", 30)
    ]
)
def test_log_level_case_insensitive(level, value):
    cls = build_config(LogLevel())
    config = cls(ATTR=level)
    assert config.attr == value


@pytest.mark.parametrize(
    "value",
    ["false", "FALSE", "some", "", str(uuid4())]
)
def test_falsy_debug(value):
    cls = build_config(DebugFlag())
    config = cls(ATTR=value)
    assert not config.attr


def test_truthy_debug():
    cls = build_config(DebugFlag())
    config = cls(ATTR='true')
    assert config.attr