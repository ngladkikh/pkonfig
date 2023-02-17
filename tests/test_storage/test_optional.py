from pkonfig.storage import Yaml, Toml


def test_yaml():
    storage = Yaml("tests/test_storage/test.yaml")
    data = {
        "str": "some",
        "int": 1,
        "float": 0.33,
    }
    for key, value in data.items():
        assert storage[key] == value
    assert storage["inner__key"] == "value"


def test_toml():
    storage = Toml("tests/test_storage/test.toml")
    data = {
        'FIRST_SECTION__STRING': 'some',
        'FIRST_SECTION__INT': 1,
        'FIRST_SECTION__FLOAT': 0.33,
        'SECOND_SECTION__KEY': 'value',
        'OBJECT__INNER__TEST_KEY': 'value'
    }
    for key, value in data.items():
        assert storage[key] == value
