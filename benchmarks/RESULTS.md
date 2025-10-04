# pkonfig vs Pydantic Settings Benchmark Results

This document presents the results of benchmarking pkonfig against Pydantic Settings in various scenarios.

## Summary

| Scenario | pkonfig (seconds) | Pydantic (seconds) | Faster | Times Faster |
|----------|-------------------|-------------------|--------|--------------|
| Simple Configuration | 0.000007 | 0.000087 | pkonfig | 13.34x |
| Nested Configuration | 0.000015 | 0.000395 | pkonfig | 26.94x |
| Large Configuration | 0.000092 | 0.000120 | pkonfig | 1.30x |
| Access Performance | 0.000001 | 0.000000 | pydantic | 7.61x |
| Dictionary Source | 0.000017 | 0.000336 | pkonfig | 19.67x |

## Analysis

### Initialization Performance

pkonfig significantly outperforms Pydantic Settings in configuration initialization across most scenarios:

1. **Simple Configuration**: pkonfig is over 13x faster when initializing a simple configuration with a few fields from environment variables.
2. **Nested Configuration**: The performance gap widens to nearly 27x faster for pkonfig when dealing with nested configuration structures.
3. **Large Configuration**: With 100 fields, pkonfig maintains a slight edge, being 1.3x faster than Pydantic.
4. **Dictionary Source**: When loading configuration from a dictionary, pkonfig is almost 20x faster than Pydantic.

### Access Performance

Pydantic Settings outperforms pkonfig in accessing configuration values once they're loaded:

- Pydantic is approximately 7.6x faster than pkonfig when accessing configuration values.
- This suggests that while pkonfig has optimized initialization, Pydantic has optimized attribute access.

## Interpretation

These results suggest that:

1. **pkonfig excels at initialization**: If your application initializes configuration objects frequently or has complex configuration structures, pkonfig offers significant performance advantages.

2. **Pydantic excels at access**: If your application accesses configuration values very frequently after initialization, Pydantic might offer better performance.

3. **Overall performance**: In most real-world scenarios, configuration is initialized once and accessed many times. The initialization performance advantage of pkonfig may be less important than the access performance advantage of Pydantic, depending on your specific use case.

4. **Scaling with complexity**: pkonfig's performance advantage is most pronounced with nested configurations, suggesting it scales better with configuration complexity.

## Considerations

When choosing between pkonfig and Pydantic Settings, consider:

1. **Initialization frequency**: How often do you create new configuration objects?
2. **Access frequency**: How often do you read configuration values?
3. **Configuration complexity**: How complex is your configuration structure?
4. **Feature requirements**: What features beyond performance do you need?

## Methodology

Each benchmark scenario was run multiple times (1000 iterations for most scenarios, 100 for the large configuration scenario) to get statistically significant results. The benchmarks measured the time it takes to:

1. Create a configuration object from various sources
2. Access configuration values

The environment was reset between benchmark scenarios to ensure clean results.

## Raw Data

For the complete benchmark data, see the `benchmark_results.json` file.