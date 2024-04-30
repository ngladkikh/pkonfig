import pytest

from pkonfig import Toml


@pytest.mark.parametrize(
    "path, value",
    (
        (("first_section", "string"), "some"),
        (("first_section", "int"), 1),
        (("first_section", "float"), 0.33),
        (("second_section", "key"), "value"),
        (("object", "inner", "test_key"), "other"),
    ),
)
def test_toml(path, value, toml_storage):
    assert toml_storage[path] == value


@pytest.fixture(scope="module")
def toml_storage():
    return Toml("tests/unit/test_storage/test.toml")
