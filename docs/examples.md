# PKonfig Examples (End-to-End)

```{eval-rst}
.. meta::
   :description: End-to-end PKonfig examples combining env vars, .env files, and YAML/TOML/INI with nested configs.
   :keywords: pkonfig examples, end to end, yaml, toml, ini, env, dotenv
```

- Web service with ENV > YAML
  ```python
  # app_config.py
  from pkonfig.config import Config
  from pkonfig import storage

  class DB(Config):
      host: str
      port: int = 5432

  class Service(Config):
      debug = False
      host = "0.0.0.0"
      port = 8000
      db = DB(alias="db")

  config = Service(
      storage.Env(prefix="APP"),
      storage.Yaml("settings.yaml", missing_ok=True),
  )
  ```

  ```yaml
  # settings.yaml
  debug: false
  host: 127.0.0.1
  port: 8000
  db:
    host: db.local
    port: 5432
  ```

  Run: `APP_PORT=9001 python -c "from app_config import config; print(config.port)"` → 9001

- Local development with .env
  ```ini
  # .env
  APP_DEBUG=true
  APP_DB_HOST=localhost
  ```
  ```python
  from pkonfig.config import Config
  from pkonfig.storage import Env, DotEnv

  class Dev(Config):
      debug: bool
      db_host: str

  config = Dev(DotEnv(".env"), Env(prefix="APP"))
  ```
