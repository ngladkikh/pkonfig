# pkonfig vs Pydantic Settings Benchmarks

This directory contains benchmarks comparing the performance of pkonfig and Pydantic Settings in various scenarios.

## Overview

The benchmarks compare pkonfig and Pydantic Settings in the following scenarios:

1. **Simple Configuration**: Basic configuration with a few fields loaded from environment variables
2. **Nested Configuration**: Hierarchical configuration with nested objects
3. **Large Configuration**: Configuration with many fields (100) to test scalability
4. **Access Performance**: Testing the performance of accessing configuration values
5. **Dictionary Source**: Loading configuration from a dictionary instead of environment variables

## Running the Benchmarks

To run the benchmarks, make sure you have both pkonfig and Pydantic installed:

```bash
pip install pydantic pydantic-settings
```

Then run the benchmark script:

```bash
python benchmarks/benchmark_pkonfig_vs_pydantic.py
```

The script will output the benchmark results to the console and save them to a JSON file (`benchmark_results.json`).

## Methodology

Each benchmark scenario is run multiple times (1000 iterations for most scenarios, 100 for the large configuration scenario) to get statistically significant results. The following metrics are collected:

- Average execution time
- Median execution time
- Minimum execution time
- Maximum execution time

The benchmarks measure the time it takes to:
1. Create a configuration object from various sources
2. Access configuration values

## Interpreting the Results

The benchmark results show the performance difference between pkonfig and Pydantic Settings in each scenario. A lower execution time indicates better performance.

The summary at the end of the benchmark run shows which library is faster in each scenario and by how much.

## Notes

- The benchmarks are designed to be fair and representative of real-world usage patterns.
- Both libraries are used according to their recommended practices.
- The environment is reset between benchmark scenarios to ensure clean results.
- The benchmarks focus on performance and do not evaluate other aspects like feature set, API design, or ease of use.