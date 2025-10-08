# PKonfig Concepts and Glossary

```{eval-rst}
.. meta::
   :description: Core concepts behind PKonfig — Config classes, Fields, Storages, Precedence, Validation, and Aliases.
   :keywords: pkonfig concepts, glossary, precedence, storages, fields, validation
```

- Config
  - Base class you subclass to declare configuration. Contains field descriptors and optional nested Configs.

- Field
  - Descriptor that defines type, default, and validation. Examples: `Str`, `Int`, `Bool`, `Choice`, `ListField`, `LogLevel`.

- Storage
  - Source of values. Implementations flatten keys into tuples, e.g., `("db", "host")`. Built-ins: `Env`, `DotEnv`, `Yaml`, `Json`, `Toml`, `Ini`, plus `DictStorage` for in-memory values.

- Precedence
  - Storages are checked left-to-right. The first storage holding a key wins.

- Aliases
  - Namespaces for nested Configs so you can have `APP_DB_HOST` map to `cfg.db.host`.

- Validation
  - Fields cast and validate values. Missing required values or failed casts raise clear exceptions.

- Fail-fast
  - By default, PKonfig validates at construction (`fail_fast=True`). Set `fail_fast=False` to defer, and call `cfg.check()` later.

- Type annotations
  - PKonfig embraces Python type hints for clean, dev-friendly configs. Always annotate your fields (e.g., host: str). Field descriptors still provide runtime casting/validation.

- Example putting it together
  ```python
  from pkonfig.config import Config
  from pkonfig import storage

  class DB(Config):
      host: str
      port: int

  class App(Config):
      debug = False
      db: DB

  cfg = App(storage.Env(prefix="APP"))
  ```

- See also
  - Quickstart for minimal setup
  - Tutorials for deep dives
  - API for full reference
