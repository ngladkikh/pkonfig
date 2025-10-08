# pkonfig vs Pydantic Settings Benchmark Results

This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.

## Summary

| Scenario | pkonfig (µs) | Pydantic (µs) | Faster | Times Faster |
|----------|----------------|----------------|--------|--------------|
| Simple Configuration | 8.965 | 75.632 | pkonfig | 8.44x |
| Nested Configuration | 6.741 | 340.237 | pkonfig | 50.48x |
| Large Configuration | 52.084 | 91.105 | pkonfig | 1.75x |
| Access Performance | 1.353 | 0.108 | pydantic | 12.54x |
| Dictionary Source | 10.759 | 277.819 | pkonfig | 25.82x |

## Methodology

These benchmarks run multiple iterations per scenario and report average times.
See benchmarks/README.md for details and how to reproduce.

The raw JSON is saved to `benchmarks/benchmark_results.json`.
