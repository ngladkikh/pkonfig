"""
Large configuration benchmark scenario.
"""
import os
from typing import Dict, Any

from pydantic_settings import BaseSettings

from pkonfig import Config, Str, Env
from benchmarks.utils import run_benchmark

def benchmark_large_config() -> Dict[str, Any]:
    """
    Benchmark scenario: Large configuration with many fields.
    
    Returns:
        Dictionary with benchmark results
    """
    # Create a dictionary with many fields
    large_dict = {f"field_{i}": f"value_{i}" for i in range(100)}

    # Set environment variables
    for key, value in large_dict.items():
        os.environ[f"APP_{key.upper()}"] = value

    # pkonfig implementation
    class PkonfigLargeConfig(Config):
        pass

    # Dynamically add fields to pkonfig class
    for i in range(100):
        setattr(PkonfigLargeConfig, f"field_{i}", Str(f"default_value_{i}"))

    # Pydantic implementation
    class PydanticLargeConfig(BaseSettings):
        model_config = {
            "env_prefix": "APP_"
        }

    # Dynamically add fields to pydantic class
    for i in range(100):
        setattr(PydanticLargeConfig, f"field_{i}", (str, ...))

    # Benchmark pkonfig
    def create_pkonfig_large_config():
        return PkonfigLargeConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_large_config():
        return PydanticLargeConfig()

    pkonfig_result = run_benchmark("Large Config - pkonfig", create_pkonfig_large_config, iterations=100)
    pydantic_result = run_benchmark("Large Config - pydantic", create_pydantic_large_config, iterations=100)

    return {
        "scenario": "Large Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }