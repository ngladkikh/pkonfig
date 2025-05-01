"""
Benchmark comparing attrs-based configs with pydantic-settings.
This benchmark focuses on field access performance.
"""
import os
import json
from typing import Dict, Any, Tuple

from pydantic_settings import BaseSettings

from pkonfig.attrs import Config, Str, Int, Bool
from pkonfig.storage import Env
from benchmarks.utils import run_benchmark

# Attrs-based config implementation
class AttrsConfig(Config):
    name: str = Str("DefaultName")
    debug: bool = Bool(False)
    port: int = Int(8000)
    version: str = Str("1.0.0")
    host: str = Str("localhost")

# Pydantic-settings implementation
class PydanticConfig(BaseSettings):
    name: str = "DefaultName"
    debug: bool = False
    port: int = 8000
    version: str = "1.0.0"
    host: str = "localhost"

    model_config = {
        "env_prefix": "APP_"
    }

def benchmark_field_access() -> Dict[str, Any]:
    """
    Benchmark the field access time of attrs-based config and pydantic-settings.

    Returns:
        Dictionary with benchmark results
    """
    # Set up environment variables
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_PORT"] = "8080"
    os.environ["APP_VERSION"] = "2.0.0"
    os.environ["APP_HOST"] = "example.com"

    # Create instances
    attrs_config = AttrsConfig(Env(prefix="APP"))
    pydantic_config = PydanticConfig()

    # Benchmark attrs-based access
    def access_attrs() -> Tuple[str, bool, int, str, str]:
        name = attrs_config.name
        debug = attrs_config.debug
        port = attrs_config.port
        version = attrs_config.version
        host = attrs_config.host
        return name, debug, port, version, host

    # Benchmark pydantic access
    def access_pydantic() -> Tuple[str, bool, int, str, str]:
        name = pydantic_config.name
        debug = pydantic_config.debug
        port = pydantic_config.port
        version = pydantic_config.version
        host = pydantic_config.host
        return name, debug, port, version, host

    # Run benchmarks with more iterations for better accuracy
    attrs_result = run_benchmark("Field Access - Attrs", access_attrs, iterations=100000)
    pydantic_result = run_benchmark("Field Access - Pydantic", access_pydantic, iterations=100000)

    # Compare results
    attrs_avg = attrs_result["average"]
    pydantic_avg = pydantic_result["average"]

    if attrs_avg < pydantic_avg:
        faster = "Attrs"
        times_faster = pydantic_avg / attrs_avg
    else:
        faster = "Pydantic"
        times_faster = attrs_avg / pydantic_avg

    print(f"\n=== FIELD ACCESS COMPARISON ===")
    print(f"Attrs: {attrs_avg:.9f} seconds")
    print(f"Pydantic: {pydantic_avg:.9f} seconds")
    print(f"{faster} field access is {times_faster:.2f}x faster")

    return {
        "scenario": "Field Access Performance",
        "attrs": attrs_result,
        "pydantic": pydantic_result,
        "comparison": {
            "faster": faster,
            "times_faster": times_faster
        }
    }

def benchmark_attrs_vs_pydantic() -> Dict[str, Any]:
    """
    Benchmark scenario: Compare attrs-based configs with pydantic-settings.
    This benchmark focuses on field access performance.

    Returns:
        Dictionary with benchmark results
    """
    # Run the field access benchmark
    access_results = benchmark_field_access()

    # Save results to file
    with open("benchmark_attrs_vs_pydantic.json", "w") as f:
        json.dump(access_results, f, indent=2)

    print("\nBenchmark results saved to benchmark_attrs_vs_pydantic.json")

    return access_results

if __name__ == "__main__":
    benchmark_attrs_vs_pydantic()
