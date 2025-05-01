# Benchmark: Descriptors vs Attrs

This benchmark compares the performance of the current descriptor-based field implementation in pkonfig with an alternative implementation using Python's attrs library.

## Benchmark Setup

This benchmark focuses only on field access performance:

- **Field Access Performance**: Time to access fields from an already initialized config object

Both implementations provide similar functionality:
- Loading values from environment variables
- Type conversion
- Default values
- Caching

## Results

### Field Access Performance

| Implementation | Average Time (seconds) |
|----------------|------------------------|
| Descriptors    | 0.000000987            |
| Attrs          | 0.000000110            |

**Attrs field access is 8.94x faster**

## Analysis

The benchmark results show that the attrs-based implementation is significantly faster than the descriptor-based implementation for field access:

**Field Access**: Attrs is about 8.94x faster at accessing fields. This is a significant performance difference and is likely because attrs simply accesses instance attributes directly through properties, while descriptors involve more complex method calls and logic for each access.

## Conclusion

Using attrs instead of custom descriptors would significantly improve performance for field access operations (8.94x faster). The performance improvement is substantial enough that it would be noticeable in applications that make frequent use of configuration values.

However, it's important to note that this performance improvement comes with trade-offs:

1. **Flexibility**: The descriptor-based approach provides more flexibility for implementing custom behavior during field access and assignment.

2. **Validation**: The descriptor-based approach makes it easier to implement complex validation logic that runs when fields are accessed or assigned.

3. **Lazy Loading**: The descriptor-based approach naturally supports lazy loading of values, which can be beneficial for large configurations.

If these features are not critical for your use case, switching to attrs would provide a significant performance boost.

## Implementation Details

The benchmark code can be found in `benchmarks/benchmark_descriptors_vs_attrs.py`. The full results are saved in `benchmark_descriptors_vs_attrs.json`.

The descriptor-based implementation uses the standard `Config` class with `Field` descriptors and `Env` storage. The attrs-based implementation is simplified to focus only on field access performance, directly accessing environment variables without using `BaseStorage`. This approach allows us to measure the raw performance difference in field access between descriptors and attrs properties.
