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

## Prerequisites

- Pythonic configuration management helpers.
- Multiple sources of configs (environment variables, dotenv files, YAML, JSON, TOML, INI)
  with agile order configuration.
- Configs validation mechanics based on type hints or user-defined classes.
- Minimal external dependencies.
- Follow [the Fail-fast](https://en.wikipedia.org/wiki/Fail-fast) principle.
- Autocomplete in modern IDEs.

## Features

- User-defined config source order: Define the order in which PKonfig looks for configuration values.
- Multilevel configs for environment variables and dotenv config sources: Allows for more granular control over configuration values.
- Custom aliases for fields or groups of configs: Create custom aliases for configuration values to make them easier to reference in code.
- Configs type casting: Automatically cast configuration values to the correct data type.
- Config values validation based on type and/or value: Validate configuration values to ensure they meet specific requirements.
- High performance: Designed to be fast and efficient.
- Extendable API: Easily extend PKonfig to meet your specific needs.


