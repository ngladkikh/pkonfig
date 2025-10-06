# Quickstart

The Config class is a Pythonic configuration management helper designed
to provide a simple way of managing multiple sources of configuration values in your application.
The most basic usage example is when environment variables are used for the production
environment and DotEnv files are used for local development.

Create config module `config.py`:

```python
from typing import Literal
from pkonfig import Config, LogLevel, Choice, Str, Int
from pkonfig.storage import Env
from pkonfig import DotEnv


class PG(Config):
    host: str = Str("localhost")
    port: int = Int(5432)
    user: str = Str("postgres")
    password: str = Str("postgres")


class AppConfig(Config):
    db1 = PG()
    db2 = PG()
    log_level: int = LogLevel("INFO")
    env: Literal["local", "prod", "test"] = Choice(["local", "prod", "test"], default="prod")


config = AppConfig(DotEnv(".env"), Env())
```

For local development create DotEnv file in root app folder `.env`:

```ini
APP_DB1_HOST=10.10.10.10
APP_DB1_USER=user
APP_DB1_PASSWORD=securedPass
APP_ENV=local
APP_LOG_LEVEL=debug
```

Then elsewhere in app you could run:

```python
from config import config

print(config.env)           # 'local'
print(config.log_level)     # 20
print(config.db.host)       # 'localhost'
print(config.db.port)       # 5432
print(config.db.user)       # 'postgres'
print(config.db.password)   # 'postgres'
```
