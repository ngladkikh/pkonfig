import json

from benchmarks.scenarios import (
    benchmark_access_performance,
    benchmark_dict_source,
    benchmark_large_config,
    benchmark_nested_config,
    benchmark_simple_config,
)


def main():
    print("Running benchmarks comparing pkonfig and Pydantic Settings...")

    results = []

    # Run all benchmarks
    results.append(benchmark_simple_config())
    results.append(benchmark_nested_config())
    results.append(benchmark_large_config())
    results.append(benchmark_access_performance())
    results.append(benchmark_dict_source())

    # Print summary
    print("\n=== BENCHMARK SUMMARY ===")
    for result in results:
        scenario = result["scenario"]
        pkonfig_avg = result["pkonfig"]["average"]
        pydantic_avg = result["pydantic"]["average"]

        if pkonfig_avg < pydantic_avg:
            faster = "pkonfig"
            times_faster = pydantic_avg / pkonfig_avg
        else:
            faster = "pydantic"
            times_faster = pkonfig_avg / pydantic_avg

        print(f"{scenario}:")
        print(f"  pkonfig: {pkonfig_avg:.6f} seconds")
        print(f"  pydantic: {pydantic_avg:.6f} seconds")
        print(f"  {faster} is {times_faster:.2f}x faster")
        print()

    # Save results to JSON file
    with open("benchmarks/benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Benchmark results saved to benchmark_results.json")


if __name__ == "__main__":
    main()
