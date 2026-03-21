import sys

import pytest

if sys.version_info < (3, 10):
    pytestmark = pytest.mark.skip(
        reason="Pydantic Settings integration requires Python 3.10+"
    )
else:
    from pydantic import AliasChoices, BaseModel, Field, ValidationError

    from pkonfig import DictStorage
    from pkonfig.pydantic_settings import (
        PKonfigBaseSettings,
        pkonfig_settings_config,
    )


def test_settings_load_values_from_pkonfig_storage():
    class Settings(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(
            DictStorage(app_name="billing", port="8080", debug="true")
        )

        app_name: str
        port: int
        debug: bool = False

    settings = Settings()

    assert settings.app_name == "billing"
    assert settings.port == 8080
    assert settings.debug is True


def test_settings_use_pkonfig_storage_precedence():
    class Settings(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(
            DictStorage(region="eu-central-1"),
            DictStorage(region="us-east-1"),
        )

        region: str

    settings = Settings()

    assert settings.region == "eu-central-1"


def test_settings_support_nested_models():
    class Database(BaseModel):
        host: str
        port: int

    class Settings(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(
            DictStorage(database={"host": "db.internal", "port": "5432"})
        )

        database: Database

    settings = Settings()

    assert settings.database.host == "db.internal"
    assert settings.database.port == 5432


def test_settings_support_validation_aliases():
    class Settings(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(DictStorage(service_name="warehouse"))

        app_name: str = Field(validation_alias=AliasChoices("service_name", "app_name"))

    settings = Settings()

    assert settings.app_name == "warehouse"


def test_init_values_override_pkonfig_storages():
    class Settings(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(DictStorage(port="7000"))

        port: int

    settings = Settings(port=9000)

    assert settings.port == 9000


def test_native_pydantic_sources_are_opt_in_when_pkonfig_storages_are_configured(
    monkeypatch,
):
    monkeypatch.setenv("PORT", "9100")

    class WithoutNativeSources(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(DictStorage())

        port: int

    class WithNativeSources(PKonfigBaseSettings):
        model_config = pkonfig_settings_config(
            DictStorage(),
            use_native_sources=True,
        )

        port: int

    try:
        WithoutNativeSources()
    except ValidationError:
        pass
    else:  # pragma: no cover - defensive
        raise AssertionError(
            "Expected settings validation to fail without native sources"
        )

    settings = WithNativeSources()

    assert settings.port == 9100
