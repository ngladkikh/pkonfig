"""
Benchmark comparing descriptor-based fields with attrs-based fields.
This benchmark focuses only on field access performance.
"""
import os
import json
import attr
from typing import Dict, Any, Tuple

from pkonfig import Config, Str, Int, Bool, Env
from benchmarks.utils import run_benchmark

# Current descriptor-based implementation
class DescriptorConfig(Config):
    name: str = Str("DefaultName")
    debug: bool = Bool(False)
    port: int = Int(8000)
    version: str = Str("1.0.0")
    host: str = Str("localhost")

# Simplified attrs-based implementation
@attr.s(auto_attribs=True)
class AttrsConfig:
    name: str = "DefaultName"
    debug: bool = False
    port: int = 8000
    version: str = "1.0.0"
    host: str = "localhost"
    _cache: Dict[str, Any] = attr.ib(factory=dict)
    _prefix: str = attr.ib(default="APP")

    def __attrs_post_init__(self):
        # Load values from environment
        self._load_from_env()

    def _load_from_env(self):
        """Load values from environment variables"""
        env_vars = {
            "name": f"{self._prefix}_NAME",
            "debug": f"{self._prefix}_DEBUG",
            "port": f"{self._prefix}_PORT",
            "version": f"{self._prefix}_VERSION",
            "host": f"{self._prefix}_HOST",
        }

        for attr_name, env_var in env_vars.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                # Simple type conversion
                if attr_name == "debug":
                    value = value.lower() in ("true", "yes", "y", "1", "+")
                elif attr_name == "port":
                    value = int(value)
                # Store in cache
                self._cache[attr_name] = value

    @property
    def name(self) -> str:
        return self._cache.get("name", self.name)

    @property
    def debug(self) -> bool:
        return self._cache.get("debug", self.debug)

    @property
    def port(self) -> int:
        return self._cache.get("port", self.port)

    @property
    def version(self) -> str:
        return self._cache.get("version", self.version)

    @property
    def host(self) -> str:
        return self._cache.get("host", self.host)

# Initialization benchmark removed as per requirements

def benchmark_field_access() -> Dict[str, Any]:
    """
    Benchmark the field access time of descriptor-based and attrs-based configs.

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
    descriptor_config = DescriptorConfig(Env(prefix="APP"))
    attrs_config = AttrsConfig()  # Simplified implementation

    # Benchmark descriptor-based access
    def access_descriptor() -> Tuple[str, bool, int, str, str]:
        name = descriptor_config.name
        debug = descriptor_config.debug
        port = descriptor_config.port
        version = descriptor_config.version
        host = descriptor_config.host
        return name, debug, port, version, host

    # Benchmark attrs-based access
    def access_attrs() -> Tuple[str, bool, int, str, str]:
        name = attrs_config.name
        debug = attrs_config.debug
        port = attrs_config.port
        version = attrs_config.version
        host = attrs_config.host
        return name, debug, port, version, host

    # Run benchmarks with more iterations for better accuracy
    descriptor_result = run_benchmark("Field Access - Descriptors", access_descriptor, iterations=100000)
    attrs_result = run_benchmark("Field Access - Attrs", access_attrs, iterations=100000)

    # Compare results
    descriptor_avg = descriptor_result["average"]
    attrs_avg = attrs_result["average"]

    if descriptor_avg < attrs_avg:
        faster = "Descriptors"
        times_faster = attrs_avg / descriptor_avg
    else:
        faster = "Attrs"
        times_faster = descriptor_avg / attrs_avg

    print(f"\n=== FIELD ACCESS COMPARISON ===")
    print(f"Descriptors: {descriptor_avg:.9f} seconds")
    print(f"Attrs: {attrs_avg:.9f} seconds")
    print(f"{faster} field access is {times_faster:.2f}x faster")

    return {
        "scenario": "Field Access Performance",
        "descriptor": descriptor_result,
        "attrs": attrs_result,
        "comparison": {
            "faster": faster,
            "times_faster": times_faster
        }
    }

# First access benchmark removed as per requirements

def benchmark_descriptors_vs_attrs() -> Dict[str, Any]:
    """
    Benchmark scenario: Compare descriptor-based fields with attrs-based fields.
    This benchmark focuses only on field access performance.

    Returns:
        Dictionary with benchmark results
    """
    # Run only the field access benchmark
    access_results = benchmark_field_access()

    # Save results to file
    with open("benchmark_descriptors_vs_attrs.json", "w") as f:
        json.dump(access_results, f, indent=2)

    print("\nBenchmark results saved to benchmark_descriptors_vs_attrs.json")

    return access_results

if __name__ == "__main__":
    benchmark_descriptors_vs_attrs()
