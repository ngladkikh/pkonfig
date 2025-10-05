"""
Access performance benchmark scenario.
"""

import os
from typing import Any, Dict, Tuple

from pydantic_settings import BaseSettings

from benchmarks.utils import run_benchmark
from pkonfig import Bool, Config, Env, Int, Str


def benchmark_access_performance() -> Dict[str, Any]:
    """
    Benchmark scenario: Access performance of configuration objects.

    Returns:
        Dictionary with benchmark results
    """
    # Set up environment variables
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_PORT"] = "8080"

    # pkonfig implementation
    class PkonfigAccessConfig(Config):
        name: str = Str("DefaultName")
        debug: bool = Bool(False)
        port: int = Int(8000)

    # Pydantic implementation
    class PydanticAccessConfig(BaseSettings):
        name: str
        debug: bool
        port: int

        model_config = {"env_prefix": "APP_"}

    # Create instances
    pkonfig_config = PkonfigAccessConfig(Env(prefix="APP"))
    pydantic_config = PydanticAccessConfig()

    # Benchmark pkonfig access
    def access_pkonfig() -> Tuple[str, bool, int]:
        name = pkonfig_config.name
        debug = pkonfig_config.debug
        port = pkonfig_config.port
        return name, debug, port

    # Benchmark pydantic access
    def access_pydantic() -> Tuple[str, bool, int]:
        name = pydantic_config.name
        debug = pydantic_config.debug
        port = pydantic_config.port
        return name, debug, port

    pkonfig_result = run_benchmark(
        "Access Performance - pkonfig", access_pkonfig, iterations=10000
    )
    pydantic_result = run_benchmark(
        "Access Performance - pydantic", access_pydantic, iterations=10000
    )

    return {
        "scenario": "Access Performance",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result,
    }
