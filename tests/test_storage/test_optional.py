from pkonfig.storage import Yaml, Toml


def test_yaml():
    storage = Yaml("tests/test_storage/test.yaml")
    assert storage == {
        "str": "some",
        "int": 1,
        "float": 0.33,
        "inner": {"key": "value"}
    }


def test_toml():
    storage = Toml("tests/test_storage/test.toml")
    assert storage == {
        "first_section": {
            "string": "some",
            "int": 1,
            "float": 0.33,
        },
        "second_section": {"key": "value"},
        "object": {"inner": {"test_key": "value"}}
    }
