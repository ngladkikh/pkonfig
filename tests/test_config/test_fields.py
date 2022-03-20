from enum import Enum, auto

import pytest

from pkonfig.base import BaseOuterConfig
from pkonfig.fields import (
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


def build_config(descriptor) -> "Config":
    class Config(BaseOuterConfig):
        attr = descriptor

        def __init__(self, **kwargs):
            super().__init__(kwargs)

    return Config


@pytest.fixture
def int_config():
    cls = build_config(Int())
    return cls(attr=3)


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
    config = cls(attr=2)
    assert config.attr == "2"


def test_path_cast():
    cls = build_config(PathField(missing_ok=True))
    config = cls(attr="/some")
    assert config.attr.name == "some"


def test_path_not_exists_raises():
    cls = build_config(PathField())
    with pytest.raises(FileNotFoundError):
        cls(attr="/some")


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
        red = auto()
        green = auto()
        blue = auto()

    return build_config(EnumField(Color)), Color


def test_enum_param_returns_value(enum_attr_config):
    cls, enum_cls = enum_attr_config
    config = cls(attr="red")
    assert config.attr is enum_cls.red


def test_enum_raises_error(enum_attr_config):
    enum_attr_config, _ = enum_attr_config
    with pytest.raises(KeyError):
        enum_attr_config(attr="foo")


def test_choice_raises_error():
    cls = build_config(Choice(["foo", "bar"]))
    with pytest.raises(TypeError):
        cls(attr="test")


def test_choice():
    cls = build_config(Choice(["foo", "bar"]))
    config = cls(attr="foo")
    assert config.attr == "foo"


def test_choice_casts_values():
    cls = build_config(
        Choice(
            [10, 100],
            int
        )
    )
    config = cls(attr="10")
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
    config = cls(attr=level)
    assert config.attr == value
