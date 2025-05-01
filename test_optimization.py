from benchmarks.scenarios.access_performance import benchmark_access_performance

# Run the benchmark
result = benchmark_access_performance()

# Print the results
print("\nAccess Performance Benchmark Results:")
print(f"pkonfig: {result['pkonfig']['average']} seconds")
print(f"pydantic: {result['pydantic']['average']} seconds")
print(f"Ratio (pydantic/pkonfig): {result['pydantic']['average'] / result['pkonfig']['average']}x")