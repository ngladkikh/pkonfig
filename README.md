# PKonfig

Pragmatic, type-safe configuration for Python apps. PKonfig turns scattered env vars and config files into one clean, validated object with predictable precedence and great DX.

Why PKonfig
- Avoid config spaghetti: declare your config as code, not as ad‑hoc parsing scattered around the app.
- Fail fast: catch missing or invalid values at startup, not at 2 a.m. in production.
- Predictable precedence: layer env vars, .env, YAML/JSON/TOML/INI in the order you choose.
- Type-safe by default: fields convert and validate values; your IDE autocompletion just works.
- Fast and lightweight: minimal dependencies, small surface area, no magic.
- Framework-agnostic: works equally well in CLIs, services, scripts, and jobs.

What problems it solves
- “Where does this setting come from?” → Single source of truth with clear precedence.
- “Why did prod behave differently?” → Explicit, validated defaults and fail-fast checks.
- “Why is this a string not an int?” → Built-in casting and validation for common types.

Key features
- Typed, validated configuration objects
- Multiple sources (env vars, .env, YAML, JSON, TOML, INI) with flexible precedence
- Minimal dependencies, fail-fast checks, and great IDE autocompletion
- Extensible API with high performance

Quick start
```python
from pkonfig.config import Config
from pkonfig.fields import Str, Int, Bool
from pkonfig.storage.env import Env
from pkonfig.storage.yaml_ import Yaml

class App(Config):
    host = Str(default="127.0.0.1")
    port = Int(default=8000)
    debug = Bool(default=False)

# Highest precedence first
cfg = App(
    Env(prefix="APP"),
    Yaml("config.yaml", missing_ok=True),
)

print(cfg.host, cfg.port, cfg.debug)
# Env example: APP_PORT=9000 python app.py → 9000 overrides file/defaults
```

Install
```bash
pip install pkonfig
# extras for file formats
pip install pkonfig[yaml]
pip install pkonfig[toml]
```

Documentation
- https://ngladkikh.github.io/pkonfig/

Links
- PyPI: https://pypi.org/project/pkonfig/
- Source: https://github.com/ngladkikh/pkonfig
- License: MIT