"""
Utility functions for benchmarking.
"""

import gc
import statistics
import time
from typing import Any, Callable, Dict, List, Tuple, TypeVar

T = TypeVar("T")


def measure_time(func: Callable[..., T], *args: Any, **kwargs: Any) -> Tuple[T, float]:
    """
    Measure the execution time of a function using a high‑resolution timer.

    Args:
        func: The function to measure
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        A tuple containing the function result and the execution time in seconds
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    end_time = time.perf_counter()
    return result, end_time - start_time


def run_benchmark(
    name: str,
    func: Callable[..., Any],
    iterations: int = 1000,
    *args: Any,
    warmup: int = 10,
    disable_gc: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Run a benchmark on a function multiple times and report statistics.

    Args:
        name: Name of the benchmark
        func: Function to benchmark
        iterations: Number of iterations to run
        *args: Arguments to pass to the function
        warmup: Number of warmup iterations (not measured)
        disable_gc: Disable garbage collection during timed runs to reduce noise
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Dictionary with benchmark results
    """
    # Warmup runs (not measured)
    for _ in range(max(0, warmup)):
        func(*args, **kwargs)

    # Optionally disable GC during measurement
    gc_was_enabled = gc.isenabled()
    if disable_gc and gc_was_enabled:
        gc.disable()
    try:
        times: List[float] = []
        for _ in range(iterations):
            _, execution_time = measure_time(func, *args, **kwargs)
            times.append(execution_time)
    finally:
        if disable_gc and gc_was_enabled:
            gc.enable()

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
        "iterations": iterations,
        "warmup": warmup,
        "gc_disabled": disable_gc,
    }
