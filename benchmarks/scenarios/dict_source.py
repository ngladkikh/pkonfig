"""
Dictionary source benchmark scenario.
"""
from typing import Dict, Any

from pydantic_settings import BaseSettings

from pkonfig import Config, Str, Int, Bool, DictStorage
from benchmarks.utils import run_benchmark

def benchmark_dict_source() -> Dict[str, Any]:
    """
    Benchmark scenario: Using dictionary as a configuration source.
    
    Returns:
        Dictionary with benchmark results
    """
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