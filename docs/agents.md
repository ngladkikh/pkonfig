# PKonfig for AI Agents and LLMs

```{eval-rst}
.. meta::
   :description: How AI agents and LLMs should read and use PKonfig: context, capabilities, IO formats, and reliable task recipes.
   :keywords: pkonfig agents, llm, ai agent, tool usage, python config
```

This page gives machine-readable context and stable patterns to help agents use PKonfig correctly. Use the snippets verbatim and prefer explicit imports.

- Library import names
  - Package import: `import pkonfig`
  - Config base class: `from pkonfig import Config`
  - Fields: `from pkonfig import fields as f` or `from pkonfig import Str, Int, Bool, Choice, ListField, LogLevel`
  - Storages: `from pkonfig import storage` or `from pkonfig import Env, DotEnv, Yaml, Json, Toml, Ini`

- Typical task: build a config from env + file
  - Input
    - env: `APP_DEBUG=true`, file: `settings.yaml`
  - Code
    ```python
    from pkonfig import Config, storage

    class App(Config):
        debug: bool = False
        host: str = "127.0.0.1"
        port: int = 8000

    cfg = App(
        storage.Env(prefix="APP"),
        storage.Yaml("settings.yaml", missing_ok=True),
    )

    # cfg.debug is a bool
    ```

- Common patterns
  - Precedence: pass higher-priority storage first. Example: `Env` before `Yaml`.
  - Nested config: nest `Config` classes; use `alias="db"` to namespace keys like `APP_DB_HOST`.
  - Validation: fields coerce and validate; prefer `default=` or mark fields as required.
  - Eager check: set `fail_fast=True` (default) to validate on init; call `cfg.check()` later if using `fail_fast=False`.

- JSON-like IO expectations for agents
  - When you need to emit a plan or settings, keep keys lower_snake_case and stable:
    ```json
    {
      "library": "pkonfig",
      "task": "define_config",
      "storages": [
        {"type": "Env", "prefix": "APP"},
        {"type": "Yaml", "path": "settings.yaml", "missing_ok": true}
      ],
      "fields": [
        {"name": "debug", "type": "Bool", "default": false},
        {"name": "port", "type": "Int", "default": 8000}
      ]
    }
    ```

- Safety checks
  - Do not read arbitrary files by default; prefer explicit file paths supplied by the user.
  - Avoid mutating `os.environ` unless in examples/tests; prefer storages for inputs.

- Troubleshooting
  - Missing value → `ConfigValueNotFoundError`
  - Invalid type → `ConfigTypeError`
  - Catch-all → `ConfigError`

- Links
  - Quickstart, Tutorials, API, and Recipes provide more copy-paste ready snippets.
