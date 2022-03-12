from typing import Type

import pytest

from pkonfig.base import ConfigFromStorageBase
from pkonfig.fields import (
    IntParam,
    FloatParam,
    StrParam,
    PathParam,
    File,
    Folder,
    Choice,
    EnumParam,
)


def build_config(descriptor) -> "Config":
    class Config(ConfigFromStorageBase):
        attr = descriptor
        def __init__(self, **kwargs):
            self._storage = kwargs
    return Config


@pytest.fixture
def int_config():
    cls = build_config(IntParam())
    return cls(attr=3)


def test_int_param(int_config):
    assert int_config.attr == 3


def test_only_int_accepted(int_config):
    with pytest.raises(ValueError):
        int_config.attr = 'a'


@pytest.fixture
def float_config():
    cls = build_config(FloatParam())
    return cls(attr=0.3)


def test_float_only_accepted(float_config):
    with pytest.raises(ValueError):
        float_config.attr = 'a'


def test_string_param_casts():
    cls = build_config(StrParam())
    config = cls(attr=2)
    assert config.attr == "2"
