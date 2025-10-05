"""
Utility functions for benchmarking.
"""

import statistics
import time
from typing import Any, Callable, Dict, List, Tuple, TypeVar

T = TypeVar("T")


def measure_time(func: Callable[..., T], *args: Any, **kwargs: Any) -> Tuple[T, float]:
    """
    Measure the execution time of a function.

    Args:
        func: The function to measure
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        A tuple containing the function result and the execution time in seconds
    """
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time


def run_benchmark(
    name: str,
    func: Callable[..., Any],
    iterations: int = 1000,
    *args: Any,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Run a benchmark on a function multiple times and report statistics.

    Args:
        name: Name of the benchmark
        func: Function to benchmark
        iterations: Number of iterations to run
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Dictionary with benchmark results
    """
    times: List[float] = []
    for _ in range(iterations):
        _, execution_time = measure_time(func, *args, **kwargs)
        times.append(execution_time)

    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Benchmark: {name}")
    print(f"  Average time: {avg_time:.6f} seconds")
    print(f"  Median time: {median_time:.6f} seconds")
    print(f"  Min time: {min_time:.6f} seconds")
    print(f"  Max time: {max_time:.6f} seconds")
    print()

    return {
        "name": name,
        "average": avg_time,
        "median": median_time,
        "min": min_time,
        "max": max_time,
    }
