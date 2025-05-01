from pydantic_settings import BaseSettings
import time

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
config = PydanticConfig()

# Access a field and print the result
print(f"name: {config.name}")

# Time field access
iterations = 100_000
start_time = time.time()
for _ in range(iterations):
    name = config.name
    debug = config.debug
    port = config.port
    version = config.version
    host = config.host
end_time = time.time()

print(f"Average time per access: {(end_time - start_time) / iterations:.9f} seconds")