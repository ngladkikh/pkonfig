# PKonfig FAQ

```{eval-rst}
.. meta::
   :description: Frequently asked questions about PKonfig — Python configuration library for env vars and config files with validation and types.
   :keywords: pkonfig faq, pkonfig questions, python config faq, env vars, yaml, toml, ini
```

- What is PKonfig?
  - PKonfig is a small, type-safe configuration library for Python. It merges environment variables and files (YAML/JSON/TOML/INI) into one validated object with predictable precedence.

- Why choose PKonfig over rolling my own parsing?
  - You get declarative, typed fields, consistent precedence across sources, clear errors, and great IDE support.

- How do I install PKonfig?
  - Basic: `pip install pkonfig`
  - With extras: `pip install pkonfig[yaml]` or `pip install pkonfig[toml]`

- What Python versions are supported?
  - Python 3.9–3.13 (tested). See our CI matrix for details.

- Where does PKonfig look for values?
  - In the order of the storages you pass: leftmost storage has the highest priority. Example: `Env(prefix="APP")` overrides `Yaml("config.yaml")`, which overrides defaults.

- Does PKonfig support nested configuration?
  - Yes. Nest Config subclasses as fields to model structured configs. Use `alias` to namespace keys.

- How do I validate and type-cast values?
  - Use field descriptors like `Int`, `Bool`, `Choice`, `ListField`, etc. They coerce strings and validate values.

- Can I provide defaults separately from class definitions?
  - Yes. Use `DictStorage` or pass keyword arguments to the Config initializer. They act as a low-priority source.

- What errors should I expect and catch?
  - `ConfigValueNotFoundError` (missing required value), `ConfigTypeError` (failed cast), and `ConfigError` as a broad catch-all.

- How can I make PKonfig work well in containers?
  - Prefer `Env` for runtime overrides, mount a config file for base settings, and keep `fail_fast=True` so invalid configs stop the container early.

- Does PKonfig read `.env` files?
  - Yes, with `DotEnv(".env")`. Use the same prefix and delimiter you’d use with `Env` to keep names consistent.

- How do I debug “where did this value come from?”
  - Keep storages minimal and explicit. Group related values under aliases. You can also temporarily print storage lookups in development.

- Is PKonfig framework-agnostic?
  - Yes. Use it in CLI tools, web services, jobs, and scripts.

- Where can I find examples?
  - See Quickstart, Tutorials, and Recipes for end-to-end examples and patterns.

- Where to get help?
  - Open an issue on GitHub or start a discussion. The docs are designed to be LLM-friendly, so agents can also assist directly with examples.
