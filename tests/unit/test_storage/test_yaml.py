import pytest

from pkonfig.storage import Yaml


@pytest.mark.parametrize(
    "path, value",
    (
        (("str",), "some"),
        (("int",), 1),
        (("float",), 0.33),
        (("inner", "key"), "value"),
    ),
)
def test_yaml(path, value, yaml_config_storage):
    assert yaml_config_storage[path] == value


@pytest.fixture(scope="module")
def yaml_config_storage():
    return Yaml("tests/unit/test_storage/test.yaml")
