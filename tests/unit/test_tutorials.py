import json
import logging
from enum import Enum
from pathlib import Path
from textwrap import dedent

import pytest

from pkonfig import (
    Bool,
    Choice,
    Config,
    DictStorage,
    EnumField,
    Field,
    File,
    Float,
    Int,
    LogLevel,
    Str,
)
from pkonfig.storage import DotEnv, Env, Ini
from pkonfig.storage import Json as JsonStorage
from pkonfig.storage import Toml, Yaml


def test_tutorial_dict_storage_example():
    class AppConfig(Config):
        foo = Str()

    cfg = AppConfig(DictStorage(foo="baz"))
    assert cfg.foo == "baz"


def test_tutorial_env_storage(monkeypatch):
    monkeypatch.setenv("APP_OUTER", "foo")
    monkeypatch.setenv("APP_INNER_KEY", "baz")
    monkeypatch.setenv("IGNORED", "value")

    source = Env(prefix="APP", delimiter="_")
    assert source[("outer",)] == "foo"
    assert source[("inner", "key")] == "baz"


def test_tutorial_env_without_prefix(monkeypatch):
    monkeypatch.setenv("WHATEVER", "value")

    source = Env(prefix=None)
    assert source[("whatever",)] == "value"


def test_tutorial_dotenv_file(tmp_path):
    env_file = tmp_path / "test.env"
    env_file.write_text("APP_DB_HOST=db.local\nAPP_DB_PORT=5432\n", encoding="utf-8")

    storage = DotEnv(env_file, prefix="APP", delimiter="_", missing_ok=True)
    assert storage[("db", "host")] == "db.local"
    assert storage[("db", "port")] == "5432"


def test_tutorial_ini_storage(tmp_path):
    ini_file = tmp_path / "config.ini"
    ini_file.write_text(
        dedent(
            """
            [DEFAULT]
            ServerAliveInterval = 45

            [bitbucket.org]
            User = hg
            """
        ),
        encoding="utf-8",
    )

    storage = Ini(ini_file, missing_ok=False)
    assert storage[("bitbucket.org", "User")] == "hg"
    assert storage[("bitbucket.org", "ServerAliveInterval")] == "45"


def test_tutorial_structured_file_backends(tmp_path):
    json_file = tmp_path / "config.json"
    with json_file.open("w", encoding="utf-8") as fh:
        json.dump({"debug": True}, fh)

    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text("foo: bar\n", encoding="utf-8")

    toml_file = tmp_path / "config.toml"
    toml_file.write_text('feature = "enabled"\n', encoding="utf-8")

    json_settings = JsonStorage(json_file, missing_ok=True)
    yaml_settings = Yaml(yaml_file, missing_ok=False)
    toml_settings = Toml(toml_file, missing_ok=False)

    assert json_settings[("debug",)] is True
    assert yaml_settings[("foo",)] == "bar"
    assert toml_settings[("feature",)] == "enabled"


def test_tutorial_storage_precedence(tmp_path, monkeypatch):
    dotenv_file = tmp_path / "test.env"
    dotenv_file.write_text("APP_FOO=from_dotenv\n", encoding="utf-8")

    base_yaml = tmp_path / "base.yaml"
    base_yaml.write_text(
        "foo: from_yaml\nbar: from_yaml\nbaz: from_yaml\n", encoding="utf-8"
    )

    monkeypatch.setenv("APP_BAR", "from_env")

    class AppConfig(Config):
        foo = Str()
        bar = Str()
        baz = Str()

    cfg = AppConfig(
        DotEnv(dotenv_file, missing_ok=True),
        Env(prefix="APP"),
        Yaml(base_yaml),
    )

    assert cfg.foo == "from_dotenv"
    assert cfg.bar == "from_env"
    assert cfg.baz == "from_yaml"


def test_tutorial_building_configuration_classes():
    class AppConfig(Config):
        ratio = Float()
        workers = Int(default=1)

    cfg = AppConfig(DictStorage(ratio="0.33"))
    assert cfg.ratio == pytest.approx(0.33)
    assert cfg.workers == 1


def test_tutorial_nested_configs():
    class Database(Config):
        host = Str(default="localhost")
        port = Int(default=5432)

    class App(Config):
        db = Database(alias="db")
        timezone = Str(default="UTC")

    cfg = App(DictStorage(db={"port": 6432}))
    assert cfg.db.port == 6432
    assert cfg.timezone == "UTC"


def test_tutorial_dotenv_multilevel(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP__PG__HOST=db_host\nAPP__PG__PORT=6432\nAPP__REDIS__HOST=redis\n",
        encoding="utf-8",
    )

    class Pg(Config):
        host = Str(default="localhost")
        port = Int(default=5432)

    class Redis(Config):
        host = Str(default="localhost")
        port = Int(default=6379)

    class AppConfig(Config):
        pg = Pg()
        redis = Redis()

    cfg = AppConfig(DotEnv(env_file, delimiter="__", prefix="APP"))
    assert cfg.pg.host == "db_host"
    assert cfg.pg.port == 6432
    assert cfg.redis.host == "redis"


def test_tutorial_aliases(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(
        "APP__DB__PASS=password\nAPP__MY_ALIAS=5\n",
        encoding="utf-8",
    )

    class Host(Config):
        host = Str(default="localhost")
        password = Str(alias="PASS")

    class AppConfig(Config):
        pg = Host(alias="DB")
        retries = Int(alias="MY_ALIAS", default=1)

    cfg = AppConfig(DotEnv(env_file, delimiter="__", prefix="APP"))
    assert cfg.pg.password == "password"
    assert cfg.retries == 5


def test_tutorial_type_hints_and_caching():
    class Paths(Config):
        bucket: str
        log_level: str
        config_file: Path

    cfg = Paths(
        DictStorage(bucket="assets", log_level="INFO", config_file="config.yaml")
    )
    assert cfg.bucket == "assets"
    assert cfg.log_level == "INFO"
    assert cfg.config_file == Path("config.yaml")


def test_tutorial_default_values_and_nullability():
    class MaybeConfig(Config):
        retries = Int(default=3)
        optional_token = Str(default=None)

    cfg = MaybeConfig(DictStorage(optional_token=None))
    assert cfg.retries == 3
    assert cfg.optional_token is None


def test_tutorial_nullable_example():
    class NullableExample(Config):
        retries = Int(nullable=True)

    cfg = NullableExample(DictStorage(retries=None))
    assert cfg.retries is None


def test_tutorial_custom_computed_properties():
    class FeatureFlags(Config):
        enabled = Bool(default=True)
        environment = Str(default="test")

        @property
        def is_prod(self) -> bool:
            return self.enabled and self.environment == "prod"

    cfg = FeatureFlags(DictStorage(environment="prod"))
    assert cfg.is_prod is True


def test_tutorial_custom_fields_and_validators():
    class PositiveInt(Int):
        def validate(self, value: int) -> None:  # type: ignore[override]
            if value < 0:
                raise ValueError("Only positive values accepted")

    class CommaSeparated(Field[list[str]]):
        def cast(self, raw: str) -> list[str]:
            return [part.strip() for part in raw.split(",") if part]

    class CustomConfig(Config):
        ports = PositiveInt()
        tags = CommaSeparated(default="alpha,beta")

    cfg = CustomConfig(DictStorage(ports="5"))
    assert cfg.ports == 5
    assert cfg.tags == ["alpha", "beta"]


def test_tutorial_specialised_fields():
    class Mode(Enum):
        prod = "prod"
        staging = "staging"

    class App(Config):
        mode = EnumField(Mode)
        config_path = File()
        debug_level = LogLevel(default="INFO")
        region = Choice(["us-east-1", "eu-west-1"])

    cfg = App(
        DictStorage(
            mode="prod",
            config_path=__file__,
            debug_level="warning",
            region="us-east-1",
        )
    )
    assert cfg.mode is Mode.prod
    assert cfg.config_path == Path(__file__)
    assert cfg.debug_level == logging.WARNING
    assert cfg.region == "us-east-1"


def test_tutorial_environment_specific_configuration(monkeypatch):
    config_files = {
        "prod": "configs/prod.yaml",
        "staging": "configs/staging.yaml",
        "local": "configs/local.yaml",
    }

    def resolve_config_path() -> str:
        class _Config(Config):
            env = Choice(
                ["prod", "local", "staging"], cast_function=str.lower, default="prod"
            )

        selector = _Config(Env(prefix="APP"))
        return config_files[selector.env]

    monkeypatch.setenv("APP_ENV", "STAGING")
    assert resolve_config_path() == "configs/staging.yaml"

    monkeypatch.setenv("APP_ENV", "LOCAL")
    assert resolve_config_path() == "configs/local.yaml"

    monkeypatch.delenv("APP_ENV", raising=False)
    assert resolve_config_path() == "configs/prod.yaml"
