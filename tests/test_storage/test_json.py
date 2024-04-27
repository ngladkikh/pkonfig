import json

import pytest

from pkonfig.storage import Json


def test_json_storage(json_configs, file):
    storage = Json(file)
    for key, value in json_configs.items():
        assert storage[(key,)] == value


@pytest.fixture
def json_configs(file):
    data = {
        "str": "value",
        "int": 1,
        "float": 1 / 3,
        "bool": True,
    }
    with open(file, "w") as fh:
        json.dump(data, fh)
    yield data


@pytest.fixture
def file(tmp_path):
    yield tmp_path / "config.json"
