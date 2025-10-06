# Installation

To install basic PKonfig without YAML and TOML support, run:

```bash
pip install pkonfig
```

YAML files parsing is handled with PyYAML:

```bash
pip install pkonfig[yaml]
```

TOML files are handled with Tomli/Tomllib:

```bash
pip install pkonfig[toml]
```

And if both TOML and YAML are needed:

```bash
pip install pkonfig[toml,yaml]
```

For production no .env files are needed, but proper environment variables should be set.
In case some of the required variables are missing, `ConfigValueNotFoundError` exception is raised while `AppConfig` instantiation.
