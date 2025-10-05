# pkonfig vs Pydantic Settings Benchmark Results

This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.

## Summary

| Scenario | pkonfig (ms) | Pydantic (ms) | Faster | Times Faster |
|----------|---------------|---------------|--------|--------------|
| Simple Configuration | 0.004 | 0.074 | pkonfig | 16.80x |
| Nested Configuration | 0.010 | 0.337 | pkonfig | 33.22x |
| Large Configuration | 0.062 | 0.089 | pkonfig | 1.43x |
| Access Performance | 0.001 | 0.000 | pydantic | 6.41x |
| Dictionary Source | 0.011 | 0.273 | pkonfig | 24.20x |

## Methodology

These benchmarks run multiple iterations per scenario and report average times.
See benchmarks/README.md for details and how to reproduce.

The raw JSON is saved to `benchmarks/benchmark_results.json`.
