import pytest

from pkonfig.storage import DotEnv


def test_ignores_empty_string(env_file_with_empty_line):
    storage = DotEnv(env_file_with_empty_line)
    assert storage[("DEBUG",)] == "true"


@pytest.fixture
def env_file_with_empty_line(env_file):
    with open(env_file, "w") as fh:
        fh.write("APP_DEBUG=true\n\n")
    return env_file


def test_split_only_two_parts(env_file_with_multiple_eq):
    storage = DotEnv(env_file_with_multiple_eq)
    assert storage[("magic",)] == "first=second"


@pytest.fixture
def env_file_with_multiple_eq(env_file):
    with open(env_file, "w") as fh:
        fh.write("APP_MAGIC=first=second\n")
    return env_file


def test_no_prefix_ignored(env_file_no_prefix):
    storage = DotEnv(env_file_no_prefix)
    assert storage[("env",)] == "local"
    with pytest.raises(KeyError):
        assert storage[("some",)]


def test_no_prefix_allowed(env_file_no_prefix):
    storage = DotEnv(env_file_no_prefix, prefix="")
    assert storage[("app_env",)] == "local"
    assert storage[("some",)] == "other"


@pytest.fixture
def env_file_no_prefix(env_file):
    with open(env_file, "w") as fh:
        fh.write("APP_ENV=local\nSOME=other\n")
    return env_file


@pytest.fixture
def env_file(tmp_path):
    file = tmp_path / ".env"
    return file
