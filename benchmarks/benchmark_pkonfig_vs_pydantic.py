import os
import time
import statistics
import json

# Install pydantic if not already installed
try:
    from pydantic import Field
    from pydantic_settings import BaseSettings
except ImportError:
    import subprocess
    print("Installing pydantic...")
    subprocess.check_call(["pip", "install", "pydantic", "pydantic-settings"])
    from pydantic import Field
    from pydantic_settings import BaseSettings

from pkonfig import Config, Str, Int, Bool, DictStorage, Env

# Utility functions for benchmarking
def measure_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    return result, end_time - start_time

def run_benchmark(name, func, iterations=1000, *args, **kwargs):
    times = []
    for _ in range(iterations):
        _, execution_time = measure_time(func, *args, **kwargs)
        times.append(execution_time)

    avg_time = statistics.mean(times)
    median_time = statistics.median(times)
    min_time = min(times)
    max_time = max(times)

    print(f"Benchmark: {name}")
    print(f"  Average time: {avg_time:.6f} seconds")
    print(f"  Median time: {median_time:.6f} seconds")
    print(f"  Min time: {min_time:.6f} seconds")
    print(f"  Max time: {max_time:.6f} seconds")
    print()

    return {
        "name": name,
        "average": avg_time,
        "median": median_time,
        "min": min_time,
        "max": max_time
    }

# Scenario 1: Simple configuration with environment variables
def benchmark_simple_config():
    # Set up environment variables
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_PORT"] = "8080"

    # pkonfig implementation
    class PkonfigSimpleConfig(Config):
        name: str = Str("DefaultName")
        debug: bool = Bool(False)
        port: int = Int(8000)

    # Pydantic implementation
    class PydanticSimpleConfig(BaseSettings):
        name: str
        debug: bool
        port: int

        model_config = {
            "env_prefix": "APP_"
        }

    # Benchmark pkonfig
    def create_pkonfig_config():
        return PkonfigSimpleConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_config():
        return PydanticSimpleConfig()

    pkonfig_result = run_benchmark("Simple Config - pkonfig", create_pkonfig_config, iterations=1000)
    pydantic_result = run_benchmark("Simple Config - pydantic", create_pydantic_config, iterations=1000)

    return {
        "scenario": "Simple Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }

# Scenario 2: Nested configuration
def benchmark_nested_config():
    # Set up environment variables
    os.environ["APP_DB_HOST"] = "localhost"
    os.environ["APP_DB_PORT"] = "5432"
    os.environ["APP_DB_USER"] = "postgres"
    os.environ["APP_DB_PASSWORD"] = "password"
    os.environ["APP_REDIS_HOST"] = "localhost"
    os.environ["APP_REDIS_PORT"] = "6379"

    # pkonfig implementation
    class PkonfigDbConfig(Config):
        host: str = Str("localhost")
        port: int = Int(5432)
        user: str = Str("postgres")
        password: str = Str("password")

    class PkonfigRedisConfig(Config):
        host: str = Str("localhost")
        port: int = Int(6379)

    class PkonfigNestedConfig(Config):
        db = PkonfigDbConfig()
        redis = PkonfigRedisConfig()

    # Pydantic implementation
    class PydanticDbConfig(BaseSettings):
        host: str
        port: int
        user: str
        password: str

    class PydanticRedisConfig(BaseSettings):
        host: str
        port: int

    class PydanticNestedConfig(BaseSettings):
        db: PydanticDbConfig = Field(default_factory=PydanticDbConfig)
        redis: PydanticRedisConfig = Field(default_factory=PydanticRedisConfig)

        model_config = {
            "env_nested_delimiter": "_",
            "env_prefix": "APP_"
        }

    # Benchmark pkonfig
    def create_pkonfig_nested_config():
        return PkonfigNestedConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_nested_config():
        return PydanticNestedConfig()

    pkonfig_result = run_benchmark("Nested Config - pkonfig", create_pkonfig_nested_config, iterations=1000)
    pydantic_result = run_benchmark("Nested Config - pydantic", create_pydantic_nested_config, iterations=1000)

    return {
        "scenario": "Nested Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }

# Scenario 3: Large configuration with many fields
def benchmark_large_config():
    # Create a dictionary with many fields
    large_dict = {f"field_{i}": f"value_{i}" for i in range(100)}

    # Set environment variables
    for key, value in large_dict.items():
        os.environ[f"APP_{key.upper()}"] = value

    # pkonfig implementation
    class PkonfigLargeConfig(Config):
        pass

    # Dynamically add fields to pkonfig class
    for i in range(100):
        setattr(PkonfigLargeConfig, f"field_{i}", Str(f"default_value_{i}"))

    # Pydantic implementation
    class PydanticLargeConfig(BaseSettings):
        model_config = {
            "env_prefix": "APP_"
        }

    # Dynamically add fields to pydantic class
    for i in range(100):
        setattr(PydanticLargeConfig, f"field_{i}", (str, ...))

    # Benchmark pkonfig
    def create_pkonfig_large_config():
        return PkonfigLargeConfig(Env(prefix="APP"))

    # Benchmark pydantic
    def create_pydantic_large_config():
        return PydanticLargeConfig()

    pkonfig_result = run_benchmark("Large Config - pkonfig", create_pkonfig_large_config, iterations=100)
    pydantic_result = run_benchmark("Large Config - pydantic", create_pydantic_large_config, iterations=100)

    return {
        "scenario": "Large Configuration",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }

# Scenario 4: Access performance
def benchmark_access_performance():
    # Set up environment variables
    os.environ["APP_NAME"] = "TestApp"
    os.environ["APP_DEBUG"] = "true"
    os.environ["APP_PORT"] = "8080"

    # pkonfig implementation
    class PkonfigAccessConfig(Config):
        name: str = Str("DefaultName")
        debug: bool = Bool(False)
        port: int = Int(8000)

    # Pydantic implementation
    class PydanticAccessConfig(BaseSettings):
        name: str
        debug: bool
        port: int

        model_config = {
            "env_prefix": "APP_"
        }

    # Create instances
    pkonfig_config = PkonfigAccessConfig(Env(prefix="APP"))
    pydantic_config = PydanticAccessConfig()

    # Benchmark pkonfig access
    def access_pkonfig():
        name = pkonfig_config.name
        debug = pkonfig_config.debug
        port = pkonfig_config.port
        return name, debug, port

    # Benchmark pydantic access
    def access_pydantic():
        name = pydantic_config.name
        debug = pydantic_config.debug
        port = pydantic_config.port
        return name, debug, port

    pkonfig_result = run_benchmark("Access Performance - pkonfig", access_pkonfig, iterations=10000)
    pydantic_result = run_benchmark("Access Performance - pydantic", access_pydantic, iterations=10000)

    return {
        "scenario": "Access Performance",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }

# Scenario 5: Dictionary source
def benchmark_dict_source():
    # Create a dictionary with configuration
    config_dict = {
        "name": "TestApp",
        "debug": True,
        "port": 8080,
        "db": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "password"
        }
    }

    # pkonfig implementation
    class PkonfigDbConfig(Config):
        host: str = Str("localhost")
        port: int = Int(5432)
        user: str = Str("postgres")
        password: str = Str("password")

    class PkonfigDictConfig(Config):
        name: str = Str("DefaultName")
        debug: bool = Bool(False)
        port: int = Int(8000)
        db = PkonfigDbConfig()

    # Pydantic implementation
    class PydanticDbConfig(BaseSettings):
        host: str
        port: int
        user: str
        password: str

    class PydanticDictConfig(BaseSettings):
        name: str
        debug: bool
        port: int
        db: PydanticDbConfig

    # Benchmark pkonfig
    def create_pkonfig_dict_config():
        return PkonfigDictConfig(DictStorage(**config_dict))

    # Benchmark pydantic
    def create_pydantic_dict_config():
        return PydanticDictConfig(**config_dict)

    pkonfig_result = run_benchmark("Dictionary Source - pkonfig", create_pkonfig_dict_config, iterations=1000)
    pydantic_result = run_benchmark("Dictionary Source - pydantic", create_pydantic_dict_config, iterations=1000)

    return {
        "scenario": "Dictionary Source",
        "pkonfig": pkonfig_result,
        "pydantic": pydantic_result
    }

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
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Benchmark results saved to benchmark_results.json")

if __name__ == "__main__":
    main()
