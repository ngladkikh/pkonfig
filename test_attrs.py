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

# Time field access
iterations = 1000000
start_time = time.time()
for _ in range(iterations):
    name = config.name
    debug = config.debug
    port = config.port
    version = config.version
    host = config.host
end_time = time.time()

print(f"Average time per access: {(end_time - start_time) / iterations:.9f} seconds")