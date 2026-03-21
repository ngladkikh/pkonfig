from pydantic import AliasChoices, BaseModel, Field
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource

from pkonfig import DictStorage
from pkonfig.pydantic_settings import PKonfigSettingsSource


def test_settings_load_values_from_pkonfig_storage():
    class Settings(BaseSettings):
        app_name: str
        port: int
        debug: bool = False

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                PKonfigSettingsSource(
                    settings_cls,
                    DictStorage(app_name="billing", port="8080", debug="true"),
                ),
            )

    settings = Settings()

    assert settings.app_name == "billing"
    assert settings.port == 8080
    assert settings.debug is True


def test_settings_use_pkonfig_storage_precedence():
    class Settings(BaseSettings):
        region: str

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                PKonfigSettingsSource(
                    settings_cls,
                    DictStorage(region="eu-central-1"),
                    DictStorage(region="us-east-1"),
                ),
            )

    settings = Settings()

    assert settings.region == "eu-central-1"


def test_settings_support_nested_models():
    class Database(BaseModel):
        host: str
        port: int

    class Settings(BaseSettings):
        database: Database

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                PKonfigSettingsSource(
                    settings_cls,
                    DictStorage(database={"host": "db.internal", "port": "5432"}),
                ),
            )

    settings = Settings()

    assert settings.database.host == "db.internal"
    assert settings.database.port == 5432


def test_settings_support_validation_aliases():
    class Settings(BaseSettings):
        app_name: str = Field(validation_alias=AliasChoices("service_name", "app_name"))

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                PKonfigSettingsSource(
                    settings_cls,
                    DictStorage(service_name="warehouse"),
                ),
            )

    settings = Settings()

    assert settings.app_name == "warehouse"


def test_settings_can_be_composed_with_init_source():
    class Settings(BaseSettings):
        port: int

        @classmethod
        def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
        ) -> tuple[PydanticBaseSettingsSource, ...]:
            return (
                init_settings,
                PKonfigSettingsSource(settings_cls, DictStorage(port="7000")),
            )

    settings = Settings(port=9000)

    assert settings.port == 9000
