<p align="center">
  <img src="https://raw.githubusercontent.com/ngladkikh/pkonfig/main/docs/_static/pkonfig_logo_2.png" alt="PKonfig logo" width="200">
</p>
<p align="center">
  <em>Configs for humans</em>
</p>

[![pypi](https://img.shields.io/pypi/v/pkonfig.svg)](https://pypi.python.org/pypi/pkonfig)
[![downloads](https://img.shields.io/pypi/dm/pkonfig)](https://pepy.tech/project/pkonfig)
[![versions](https://img.shields.io/pypi/pyversions/pkonfig.svg)](https://github.com/ngladkikh/pkonfig)
[![license](https://img.shields.io/github/license/ngladkikh/pkonfig.svg)](https://github.com/ngladkikh/pkonfig/blob/master/LICENSE)
[![Type Checked with Mypy](https://img.shields.io/badge/Type%20Check-Mypy-brightgreen)](https://mypy.readthedocs.io/en/stable/)
[![Code Quality - Pylint](https://img.shields.io/badge/Code%20Quality-Pylint-blue)](https://www.pylint.org/)
[![Code Style - Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
[![Code Style - isort](https://img.shields.io/badge/Code%20Style-isort-%231674b1)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/github/ngladkikh/pkonfig/branch/main/graph/badge.svg?token=VDRSB1XUFH)](https://codecov.io/github/ngladkikh/pkonfig)

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
- List values parsing with validation

Quick start
```python
from pkonfig.config import Config
from pkonfig.storage.env import Env
from pkonfig.storage.yaml_ import Yaml

class App(Config):
    host: str = "127.0.0.1"
    port: int = 8000
    debug = False

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
- For AI Agents and LLMs: https://ngladkikh.github.io/pkonfig/agents.html

Links
- PyPI: https://pypi.org/project/pkonfig/
- Source: https://github.com/ngladkikh/pkonfig
- License: MIT
