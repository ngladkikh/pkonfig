# Benchmark: attrs-based configs vs pydantic-settings

This benchmark compares the field access performance of attrs-based configs from pkonfig with pydantic-settings.

## Setup

The benchmark compares two implementations:

1. **attrs-based config** using `Config` from `pkonfig.attrs`
2. **pydantic-settings** using `BaseSettings` from `pydantic_settings`

Both implementations define a configuration class with the same fields:
- name (string)
- debug (boolean)
- port (integer)
- version (string)
- host (string)

Environment variables are set up with the prefix "APP_" for both implementations.

## Results

The benchmark measures the time it takes to access all fields in each configuration object.

| Implementation | Average Time (seconds) |
|----------------|------------------------|
| attrs-based    | 0.000000244           |
| pydantic       | 0.000000165           |

**Pydantic field access is 1.48x faster than attrs-based config field access.**

## Analysis

The results show that pydantic-settings provides faster field access compared to the attrs-based implementation in pkonfig. This is interesting because the attrs-based implementation was designed to be faster than the descriptor-based implementation.

Some possible reasons for this difference:

1. **Caching mechanism**: The attrs-based implementation uses a cache dictionary to store values, which might add some overhead compared to pydantic's direct attribute access.

2. **Type conversion**: The way type conversion is handled might differ between the two implementations, affecting performance.

3. **Validation**: The validation process might be more optimized in pydantic.

## Conclusion

For applications where field access performance is critical, pydantic-settings might be a better choice than the attrs-based implementation in pkonfig. However, the performance difference is very small (in the nanosecond range), so other factors like feature set, ease of use, and integration with the rest of the application should also be considered when choosing between these libraries.