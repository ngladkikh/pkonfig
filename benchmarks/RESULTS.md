# pkonfig vs Pydantic Settings Benchmark Results

This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.

## Summary

| Scenario | pkonfig (µs) | Pydantic (µs) | Faster | Times Faster |
|----------|----------------|----------------|--------|--------------|
| Simple Configuration | 9.300 | 106.735 | pkonfig | 11.48x |
| Nested Configuration | 21.239 | 497.376 | pkonfig | 23.42x |
| Large Configuration | 117.105 | 130.150 | pkonfig | 1.11x |
| Access Performance | 1.017 | 0.155 | pydantic | 6.55x |
| Dictionary Source | 22.040 | 397.451 | pkonfig | 18.03x |

## Methodology

These benchmarks run multiple iterations per scenario and report average times.
See benchmarks/README.md for details and how to reproduce.

The raw JSON is saved to `benchmarks/benchmark_results.json`.
