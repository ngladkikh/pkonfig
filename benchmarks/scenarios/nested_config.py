"""
Nested configuration benchmark scenario.
"""

import os
from typing import Dict, Any

from pydantic import Field
from pydantic_settings import BaseSettings

from pkonfig import Config, Str, Int, Env
from benchmarks.utils import run_benchmark


def benchmark_nested_config() -> Dict[str, Any]:
    """
    Benchmark scenario: Nested configuration with environment variables.

    Returns:
        Dictionary with benchmark results
    """
    # Set up environment variables
    os.environ["APP_DB_HOST"] = "localhost"
    os.environ["APP_DB_PORT"] = "5432"
    os.environ["APP_DB_USER"] = "postgres"
    os.environ["APP_DB_PASSWORD"] = "password"
    os.environ["APP_REDIS_HOST"] = "localhost"
    os.environ["APP_REDIS_PORT"] = "6379"

    # pkonfig implementation
    class PkonfigDbConfig(Config):
        host: str = Str("localhost")
        port: int = Int(5432)
        user: str = Str("postgres")
        password: str = Str("password")

    class PkonfigRedisConfig(Config):
        host: str = Str("localhost")
        port: int = Int(6379)

    class PkonfigNestedConfig(Config):
        db = PkonfigDbConfig()
        redis = PkonfigRedisConfig()

    # Pydantic implementation
    class PydanticDbConfig(BaseSettings):
        host: str
        port: int
        user: str
        password: str

    class PydanticRedisConfig(BaseSettings):
        host: str
        port: int

    class PydanticNestedConfig(BaseSettings):
        db: PydanticDbConfig = Field(default_factory=PydanticDbConfig)
        redis: PydanticRedisConfig = Field(default_factory=PydanticRedisConfig)

        model_config = {"env_nested_delimiter": "_", "env_prefix": "APP_"}

    # Benchmark pkonfig
    def create_pkonfig_nested_config():
        return PkonfigNestedConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_nested_config():
        return PydanticNestedConfig()

    pkonfig_result = run_benchmark(
        "Nested Config - pkonfig", create_pkonfig_nested_config, iterations=1000
    )
    pydantic_result = run_benchmark(
        "Nested Config - pydantic", create_pydantic_nested_config, iterations=1000
    )

    return {
        "scenario": "Nested Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result,
    }
