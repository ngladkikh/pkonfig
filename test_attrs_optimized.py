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

class OptimizedConfig(Config):
    name: str = Str("DefaultName")
    debug: bool = Bool(False)
    port: int = Int(8000)
    version: str = Str("1.0.0")
    host: str = Str("localhost")

    def __init__(self, storage=None):
        super().__init__(storage)
        # Pre-compute field values and store them as instance attributes with a different naming convention
        self._direct_name = self._name_value if hasattr(self, "_name_value") else self.name
        self._direct_debug = self._debug_value if hasattr(self, "_debug_value") else self.debug
        self._direct_port = self._port_value if hasattr(self, "_port_value") else self.port
        self._direct_version = self._version_value if hasattr(self, "_version_value") else self.version
        self._direct_host = self._host_value if hasattr(self, "_host_value") else self.host

# Create an instance
config = OptimizedConfig(Env(prefix="APP"))

# Access a field and print the result
print(f"name: {config.name}")

# Time direct attribute access
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
