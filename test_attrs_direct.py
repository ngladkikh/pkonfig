from pkonfig.attrs import Config, Str, Int, Bool
from pkonfig.storage import Env
import time
import os

# Set up environment variables
os.environ["APP_NAME"] = "TestApp"
os.environ["APP_DEBUG"] = "true"
os.environ["APP_PORT"] = "8080"
os.environ["APP_VERSION"] = "2.0.0"
os.environ["APP_HOST"] = "example.com"

class AttrsConfig(Config):
    name: str = Str("DefaultName")
    debug: bool = Bool(False)
    port: int = Int(8000)
    version: str = Str("1.0.0")
    host: str = Str("localhost")

# Create an instance
config = AttrsConfig(Env(prefix="APP"))

# Access a field and print the result
print(f"name: {config.name}")

# Time direct attribute access
iterations = 1000000
start_time = time.time()
for _ in range(iterations):
    name = config._name_value if hasattr(config, "_name_value") else config.name
    debug = config._debug_value if hasattr(config, "_debug_value") else config.debug
    port = config._port_value if hasattr(config, "_port_value") else config.port
    version = config._version_value if hasattr(config, "_version_value") else config.version
    host = config._host_value if hasattr(config, "_host_value") else config.host
end_time = time.time()

print(f"Average time per access: {(end_time - start_time) / iterations:.9f} seconds")