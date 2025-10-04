import typing

import pytest

from pkonfig import DictStorage
from pkonfig.config import Config
from pkonfig.fields import Field, Int, Str


def test_class_access_returns_field_descriptor():
    class TConf(Config):
        num = Int()
        name = Str()

    # Accessing via the class should return the descriptor itself
    assert isinstance(TConf.num, Field)
    assert isinstance(TConf.name, Field)

    # Accessing via instance should return the casted values
    c = TConf(DictStorage(num="42", name=1))
    assert c.num == 42
    assert c.name == "1"


def test_typed_field_annotation_runtime_access():
    class TConf(Config):
        # Using Python type annotation together with a Field default
        num: int = Int(1)
        title: str = Str("hello")

    # Accessing via instance should return T (int/str)
    c = TConf(DictStorage())
    assert isinstance(c.num, int)
    assert c.num == 1
    assert isinstance(c.title, str)
    assert c.title == "hello"

    # Storage override should still work and be cast to the annotated type.
    # Use a fresh class to avoid cross-instance cache collisions on the same Field.
    class TConf2(Config):
        num: int = Int(1)
        title: str = Str("hello")

    c2 = TConf2(DictStorage(num="7", title=123))
    assert c2.num == 7
    assert c2.title == "123"


@pytest.mark.skipif(typing.TYPE_CHECKING, reason="Only runtime behavior is tested")
def test_descriptor_can_be_inspected_from_class():
    class TConf(Config):
        num = Int()

    # Ensure we can still access descriptor attributes from the class
    assert isinstance(TConf.num, Field)
    assert hasattr(TConf.num, "alias")
