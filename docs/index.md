# PKonfig

[![pypi](https://img.shields.io/pypi/v/pkonfig.svg)](https://pypi.python.org/pypi/pkonfig)
[![downloads](https://img.shields.io/pypi/dm/pkonfig)](https://pepy.tech/project/pkonfig)
[![versions](https://img.shields.io/pypi/pyversions/pkonfig.svg)](https://github.com/ngladkikh/pkonfig)
[![license](https://img.shields.io/github/license/ngladkikh/pkonfig.svg)](https://github.com/ngladkikh/pkonfig/blob/master/LICENSE)
[![Type Checked with Mypy](https://img.shields.io/badge/Type%20Check-Mypy-brightgreen)](https://mypy.readthedocs.io/en/stable/)
[![Code Quality - Pylint](https://img.shields.io/badge/Code%20Quality-Pylint-blue)](https://www.pylint.org/)
[![Code Style - Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
[![Code Style - isort](https://img.shields.io/badge/Code%20Style-isort-%231674b1)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/github/ngladkikh/pkonfig/branch/main/graph/badge.svg?token=VDRSB1XUFH)](https://codecov.io/github/ngladkikh/pkonfig)

```{toctree}
:maxdepth: 2
:caption: Contents

installation
quickstart
tutorials
api
benchmarks
```

Pragmatic, type-safe configuration for Python apps. 
PKonfig turns scattered env vars and config files into one clean, validated object with predictable precedence and great DX.

### Why PKonfig
- Avoid config spaghetti: declare your config as code, not as ad‑hoc parsing scattered around the app.
- Fail fast: catch missing or invalid values at startup, not at 2 a.m. in production.
- Predictable precedence: layer env vars, .env, YAML/JSON/TOML/INI in the order you choose.
- Type-safe by default: fields convert and validate values; your IDE autocompletion just works.
- Fast and lightweight: minimal dependencies, small surface area, no magic.
- Framework-agnostic: works equally well in CLIs, services, scripts, and jobs.

### What problems it solves
- “Where does this setting come from?” → Single source of truth with clear precedence.
- “Why did prod behave differently?” → Explicit, validated defaults and fail-fast checks.
- “Why is this a string not an int?” → Built-in casting and validation for common types.

### Features
- Typed, validated configuration objects
- Multiple sources (env vars, .env, YAML, JSON, TOML, INI) with flexible precedence
- Minimal dependencies, fail-fast checks, and great IDE autocompletion
- Extensible API with high performance
- User-defined config source order: Define the order in which PKonfig looks for configuration values.
- Multilevel configs for environment variables and dotenv config sources: Allows for more granular control over configuration values.
- Custom aliases for fields or groups of configs: Create custom aliases for configuration values to make them easier to reference in code.
- Configs type casting: Automatically cast configuration values to the correct data type.
- Config values validation based on type and/or value: Validate configuration values to ensure they meet specific requirements.
- High performance: Designed to be fast and efficient.
- Extendable API: Easily extend PKonfig to meet your specific needs.


