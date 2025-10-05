# pkonfig vs Pydantic Settings Benchmark Results

This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.

## Summary

| Scenario | pkonfig (µs) | Pydantic (µs) | Faster | Times Faster |
|----------|----------------|----------------|--------|--------------|
| Simple Configuration | 4.384 | 74.141 | pkonfig | 16.91x |
| Nested Configuration | 10.178 | 338.947 | pkonfig | 33.30x |
| Large Configuration | 60.752 | 87.165 | pkonfig | 1.43x |
| Access Performance | 0.701 | 0.104 | pydantic | 6.71x |
| Dictionary Source | 11.055 | 273.161 | pkonfig | 24.71x |

## Methodology

These benchmarks run multiple iterations per scenario and report average times.
See benchmarks/README.md for details and how to reproduce.

The raw JSON is saved to `benchmarks/benchmark_results.json`.
