# PKonfig Recipes (Copy-Paste Patterns)

```{eval-rst}
.. meta::
   :description: Practical PKonfig patterns for common tasks: env layering, .env for dev, nested configs, choices, lists, and validation.
   :keywords: pkonfig recipes, examples, patterns, snippets, how to
```

- Env overrides file defaults
  ```python
  from pkonfig.config import Config
  from pkonfig import storage

  class App(Config):
      host: str = "127.0.0.1"
      port: int = 8000

  cfg = App(
      storage.Env(prefix="APP"),
      storage.Yaml("settings.yaml", missing_ok=True),
  )
  ```

- Nested config with alias
  ```python
  from pkonfig.config import Config

  class DB(Config):
      host: str = "localhost"
      port: int = 5432

  class App(Config):
      db = DB(alias="db")
  ```

- Required field (no default)
  ```python
  from pkonfig.config import Config

  class App(Config):
      workers: int
  ```

- Choice of environment with Literal typing
  ```python
  from typing import Literal
  from pkonfig.config import Config
  from pkonfig.fields import Choice

  class App(Config):
      env: Literal["local", "prod", "test"] = Choice(["local", "prod", "test"], default="prod")
  ```

- Parse comma-delimited list
  ```python
  from pkonfig.config import Config
  from pkonfig.storage import DictStorage

  class App(Config):
      tags: list[str]

  cfg = App(DictStorage(tags="a,b,c"))
  # cfg.tags == ["a", "b", "c"]
  ```

- Logging level from strings
  ```python
  from pkonfig.config import Config
  from pkonfig.fields import LogLevel

  class App(Config):
      log_level: int = LogLevel("INFO")
  ```

- Defer validation until later
  ```python
  from pkonfig.config import Config
  from pkonfig.fields import Int

  class App(Config):
      port: int = 8000

  cfg = App(fail_fast=False)
  # ... later
  cfg.check()
  ```
