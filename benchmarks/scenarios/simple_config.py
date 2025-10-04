"""
Simple configuration benchmark scenario.
"""

import os
from typing import Dict, Any

from pydantic import Field
from pydantic_settings import BaseSettings

from pkonfig import Config, Str, Int, Bool, Env
from benchmarks.utils import run_benchmark


def benchmark_simple_config() -> Dict[str, Any]:
    """
    Benchmark scenario: Simple configuration with environment variables.

    Returns:
        Dictionary with benchmark results
    """
    # Set up environment variables
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_PORT"] = "8080"

    # pkonfig implementation
    class PkonfigSimpleConfig(Config):
        name: str = Str("DefaultName")
        debug: bool = Bool(False)
        port: int = Int(8000)

    # Pydantic implementation
    class PydanticSimpleConfig(BaseSettings):
        name: str
        debug: bool
        port: int

        model_config = {"env_prefix": "APP_"}

    # Benchmark pkonfig
    def create_pkonfig_config():
        return PkonfigSimpleConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_config():
        return PydanticSimpleConfig()

    pkonfig_result = run_benchmark(
        "Simple Config - pkonfig", create_pkonfig_config, iterations=1000
    )
    pydantic_result = run_benchmark(
        "Simple Config - pydantic", create_pydantic_config, iterations=1000
    )

    return {
        "scenario": "Simple Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result,
    }
