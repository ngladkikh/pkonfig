from optimized_attrs_config import Config, Str, Int, Bool
from pkonfig.storage import Env
import time
import os

# Set up environment variables
os.environ["APP_NAME"] = "TestApp"
os.environ["APP_DEBUG"] = "true"
os.environ["APP_PORT"] = "8080"
os.environ["APP_VERSION"] = "2.0.0"
os.environ["APP_HOST"] = "example.com"

class OptimizedConfig(Config):
    name: str = Str("DefaultName")
    debug: bool = Bool(False)
    port: int = Int(8000)
    version: str = Str("1.0.0")
    host: str = Str("localhost")

# Create an instance
config = OptimizedConfig(Env(prefix="APP"))

# Access a field and print the result
print(f"name: {config.name}")
print(f"debug: {config.debug}")
print(f"port: {config.port}")
print(f"version: {config.version}")
print(f"host: {config.host}")

# Time property access
iterations = 1000000
start_time = time.time()
for _ in range(iterations):
    name = config.name
    debug = config.debug
    port = config.port
    version = config.version
    host = config.host
end_time = time.time()

print(f"\nProperty access time: {(end_time - start_time) / iterations:.9f} seconds")

# Compare with Pydantic
from pydantic_settings import BaseSettings

class PydanticConfig(BaseSettings):
    name: str = "DefaultName"
    debug: bool = False
    port: int = 8000
    version: str = "1.0.0"
    host: str = "localhost"

    model_config = {
        "env_prefix": "APP_"
    }

# Create an instance
pydantic_config = PydanticConfig()

# Time Pydantic access
start_time = time.time()
for _ in range(iterations):
    name = pydantic_config.name
    debug = pydantic_config.debug
    port = pydantic_config.port
    version = pydantic_config.version
    host = pydantic_config.host
end_time = time.time()

print(f"Pydantic access time: {(end_time - start_time) / iterations:.9f} seconds")