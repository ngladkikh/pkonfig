"""
Benchmark scenarios for comparing pkonfig and pydantic.
"""

from benchmarks.scenarios.simple_config import benchmark_simple_config
from benchmarks.scenarios.nested_config import benchmark_nested_config
from benchmarks.scenarios.large_config import benchmark_large_config
from benchmarks.scenarios.access_performance import benchmark_access_performance
from benchmarks.scenarios.dict_source import benchmark_dict_source

__all__ = [
    "benchmark_simple_config",
    "benchmark_nested_config",
    "benchmark_large_config",
    "benchmark_access_performance",
    "benchmark_dict_source",
]
