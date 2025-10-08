
# Tutorials

Hands-on guides that show how to assemble real PKonfig setups: compose storages, structure nested configs, and extend the library when built-ins are not enough.

- Understand which storage backend fits each source of truth.
- Layer storages with predictable precedence and sensible defaults.
- Model complex configuration trees with nested `Config` classes and aliases.
- Extend PKonfig with custom fields, descriptors, and convenience helpers.

:::{contents}
:local:
:depth: 2
:class: this-will-duplicate-information-and-it-is-still-useful-here
:::

## Prerequisites

- Install PKonfig with any extras you plan to use (`pip install pkonfig[yaml,toml]`).
- Activate a virtual environment so examples do not mutate your system interpreter.
- When examples temporarily mutate `os.environ`, clean up afterwards if you are running them in a long-lived shell.

## Configuration sources

PKonfig ships with several storage backends. They all implement the `Mapping` interface expected by `Config` and flatten nested structures into tuple keys.

### In-memory defaults with `DictStorage`

Use `DictStorage` when you want code-defined defaults or you prefer to keep sensitive values outside the class definition.

```python
from pkonfig import Config, DictStorage, Str


class AppConfig(Config):
    foo = Str()  # raises ConfigValueNotFoundError if not provided


cfg = AppConfig(DictStorage(foo="baz"))
print(cfg.foo)  # 'baz'
```

:::{tip}
`DictStorage` is also handy in unit tests because you can inject dictionaries directly instead of touching the filesystem or environment.
:::

### Environment variables (`Env`)

Environment variables are the most portable way to configure services. `Env` understands prefixes and delimiters so you can group values.

```python
from os import environ
from pkonfig.storage import Env

environ.update({
    "APP_OUTER": "foo",
    "APP_INNER_KEY": "baz",
    "IGNORED": "value",
})

source = Env(prefix="APP", delimiter="_")
print(source[("outer",)])          # foo
print(source[("inner", "key")])   # baz
```

:::{note}
Keys are matched case-insensitively. Pass `prefix=None` (or `""`) to opt out and read every variable.
:::

```python
from os import environ
from pkonfig.storage import Env

environ["WHATEVER"] = "value"
print(Env(prefix=None)[("whatever",)])  # value
```

### `.env` files (`DotEnv`)

`.env` files are convenient during local development. `DotEnv` mirrors `Env`, trimming the prefix and delimiter as it loads lines.

```
# test.env
APP_DB_HOST=db.local
APP_DB_PORT=5432
```

```python
from pkonfig.storage import DotEnv

dev_overrides = DotEnv("test.env", prefix="APP", delimiter="_", missing_ok=True)
print(dev_overrides[("db", "host")])  # db.local
```

### INI files (`Ini`)

`Ini` wraps `configparser.ConfigParser`, exposing the same configuration knobs.

```ini
# config.ini
[DEFAULT]
ServerAliveInterval = 45

[bitbucket.org]
User = hg
```

```python
from pkonfig.storage import Ini

storage = Ini("config.ini", missing_ok=False)
print(storage[("bitbucket.org", "User")])            # hg
print(storage[("bitbucket.org", "ServerAliveInterval")])  # 45
```

### JSON, YAML, and TOML

Each structured file format has a dedicated backend. Install the optional extras if you use YAML or TOML.

```python
from pkonfig.storage import Json, Toml, Yaml

json_settings = Json("config.json", missing_ok=True)
yaml_settings = Yaml("config.yaml", missing_ok=False)
toml_settings = Toml("config.toml", missing_ok=False)
```

:::{important}
`Toml` uses `tomllib` on Python ≥3.11 and falls back to `tomli` on earlier versions. Make sure the `toml` extra is installed if you target Python 3.10 or below.
:::

## Ordering storages for precedence

Storages are evaluated left-to-right, so earlier sources override later ones. Chain together as many as you need.

```python
from pkonfig import Config, DotEnv, Env, Str, Yaml


class AppConfig(Config):
    foo = Str()


cfg = AppConfig(
    DotEnv("test.env", missing_ok=True),  # developer overrides
    Env(prefix="APP"),                   # runtime overrides
    Yaml("base.yaml"),                    # defaults committed to the repo
)
```

:::{tip}
Call `cfg.get_storage().maps` to inspect the underlying `ChainMap` if you need to debug which source supplied a value.
:::

## Building configuration classes

Declare fields on subclasses of `Config`. PKonfig eagerly validates them (unless you disable `fail_fast`).

```python
from pkonfig import Config, DictStorage, Float, Int


class AppConfig(Config):
    ratio = Float()
    workers = Int(default=1)


cfg = AppConfig(DictStorage(ratio="0.33"))
print(cfg.ratio)    # 0.33
print(cfg.workers)  # 1
```

### Nested configs

Group related settings by nesting other `Config` classes.

```python
from pkonfig import Config, DictStorage, Int, Str


class Database(Config):
    host = Str(default="localhost")
    port = Int(default=5432)


class App(Config):
    db = Database(alias="db")
    timezone = Str(default="UTC")


cfg = App(DictStorage(db={"port": 6432}))
print(cfg.db.port)   # 6432
print(cfg.timezone)  # UTC
```

### Loading multilevel keys from `.env`

```python
from pkonfig import Config, DotEnv, Int, Str


class Pg(Config):
    host = Str(default="localhost")
    port = Int(default=5432)


class Redis(Config):
    host = Str(default="localhost")
    port = Int(default=6379)


class AppConfig(Config):
    pg = Pg()
    redis = Redis()


cfg = AppConfig(DotEnv(".env", delimiter="__", prefix="APP"))
print(cfg.pg.host)
print(cfg.redis.host)
```

```
# .env
APP__PG__HOST=db_host
APP__PG__PORT=6432
APP__REDIS__HOST=redis
```

### Aliases for ergonomic keys

Aliases let storages look up alternative names without changing attribute access in Python.

```python
from pkonfig import Config, DotEnv, Int, Str


class Host(Config):
    host = Str(default="localhost")
    password = Str(alias="PASS")


class AppConfig(Config):
    pg = Host(alias="DB")
    retries = Int(alias="MY_ALIAS", default=1)


cfg = AppConfig(DotEnv(".env", delimiter="__", prefix="APP"))
print(cfg.pg.password)
print(cfg.retries)
```

```
# .env
APP__DB__PASS=password
APP__MY_ALIAS=5
```

:::{hint}
Aliases are especially helpful when migrating from an older configuration naming scheme—you can keep legacy keys alive while exposing clean attribute names in code.
:::

## Field behaviour and customization

Fields encapsulate casting, validation, and caching. The snippets below highlight common patterns.

### Type hints and caching

Declaring type annotations is enough for many cases—PKonfig resolves them to appropriate fields and caches the validated result after the first access.

```python
from pathlib import Path
from pkonfig import Config, DictStorage


class Paths(Config):
    bucket: str
    log_level: str
    config_file: Path


cfg = Paths(DictStorage(bucket="assets", log_level="INFO", config_file="config.yaml"))
print(cfg.config_file)
```

#### Defining configs using only type hints

You can define required fields by annotating attributes without assigning field instances. 
PKonfig will infer sensible field types from the annotations and validate/cast values from storages.

```python
from pkonfig import Config, DictStorage


class Simple(Config):
    host: str      # required
    port: int      # required


cfg = Simple(DictStorage(host="localhost", port=5432))
assert cfg.host == "localhost"
assert cfg.port == 5432
```

Provide defaults by assigning plain Python literals to typed attributes. 
The default will be used if the value is not found in storages.

```python
from pkonfig import Config

class WithDefaults(Config):
    retries: int = 3
    region: str = "us-east-1"


cfg = WithDefaults()

assert cfg.retries == 3
assert cfg.region == "us-east-1"
```

You can also annotate with PKonfig field classes and still assign plain literals as defaults. 
This is useful when you want the behavior of a specific field (e.g., `File`, `Decimal`) while keeping a concise declaration.

```python
from pathlib import Path
from pkonfig import File, Config


class AnnotatedWithField(Config):
    foo: File = "foo.txt"


assert AnnotatedWithField().foo == Path("foo")
```

#### Nested configs with type hints

Nested configuration groups can be declared purely via type annotations by referencing other `Config` subclasses as types:

```python
from pkonfig import Config, DictStorage


class Inner(Config):
    required: int


class App(Config):
    inner: Inner  # required group


cfg = App(DictStorage(inner={"required": 1234}))
assert cfg.inner["required"] == 1234
```

You can mix instance-style and type-hint-style declarations side by side:

```python
from pkonfig import Int, Str, Config


class Inner(Config):
    foo = Str("baz", nullable=False)
    fiz = Int(123, nullable=False)
    required = Int()


class App(Config):
    inner_1 = Inner()   # instance declaration
    inner_2: Inner      # type-hint declaration
    foo = Int()
```

Each nested config attribute maintains its own independent cache even if they share the same type:

```python
from pkonfig import Config, DictStorage

class Inner(Config):
    required: int

class Duo(Config):
    i1: Inner
    i2: Inner


cfg = Duo(DictStorage(i1={"required": 1234}, i2={"required": 4321}))
assert cfg.i1["required"] == 1234
assert cfg.i2["required"] == 4321
```

#### Caching semantics for type-hinted fields

PKonfig caches the validated value after the first access. 
Subsequent changes in the underlying storage won’t affect already accessed attributes until you reconstruct the config object.

```python
from pkonfig import Config, DictStorage


class CacheDemo(Config):
    foo: str


storage = DictStorage(foo="bar")
cfg = CacheDemo(storage)

assert cfg.foo == "bar"

# Mutate the storage after access
storage._actual_storage[("foo",)] = "baz"

# Value is cached on the config instance
assert cfg.foo == "bar"
```

### Default values and nullability

```python
from pkonfig import Config, DictStorage, Int, Str


class MaybeConfig(Config):
    retries = Int(default=3)
    optional_token = Str(default=None)


cfg = MaybeConfig(DictStorage(optional_token=None))
print(cfg.retries)         # 3
print(cfg.optional_token)  # None
```

Set `nullable=True` to allow `None` without casting.

```python
from pkonfig import Config, DictStorage, Int


class NullableExample(Config):
    retries = Int(nullable=True)


cfg = NullableExample(DictStorage(retries=None))
print(cfg.retries is None)  # True
```

### Custom computed properties

```python
from pkonfig import Bool, Config, DictStorage, Str


class FeatureFlags(Config):
    enabled = Bool(default=True)
    environment = Str(default="test")

    @property
    def is_prod(self) -> bool:
        return self.enabled and self.environment == "prod"


cfg = FeatureFlags(DictStorage(environment="prod"))
print(cfg.is_prod)
```

### Custom fields and validators

Extend built-in fields when you need bespoke validation or casting.

```python
from pkonfig import Config, Field, Int


class PositiveInt(Int):
    def validate(self, value: int) -> None:
        if value < 0:
            raise ValueError("Only positive values accepted")


class CommaSeparated(Field[list[str]]):
    def cast(self, raw: str) -> list[str]:
        return [part.strip() for part in raw.split(",") if part]


class CustomConfig(Config):
    ports = PositiveInt()
    tags = CommaSeparated(default="alpha,beta")
```

## Specialised fields

PKonfig includes helpers for filesystem paths, enums, log levels, and constrained choices.

```python
from enum import Enum
from pathlib import Path
import logging

from pkonfig import Choice, Config, DictStorage, EnumField, File, LogLevel, PathField


class Mode(Enum):
    prod = "prod"
    staging = "staging"


class App(Config):
    mode = EnumField(Mode)
    config_path = File()
    debug_level = LogLevel(default="INFO")
    region = Choice(["us-east-1", "eu-west-1"])


cfg = App(
    DictStorage(
        mode="prod",
        config_path=__file__,
        debug_level="warning",
        region="us-east-1",
    )
)
print(cfg.mode, cfg.config_path, cfg.debug_level)
```

## Environment-specific configuration files

Select configuration files dynamically by reading a simple config first.

```python
from pkonfig import Choice, Config, Env


CONFIG_FILES = {
    "prod": "configs/prod.yaml",
    "staging": "configs/staging.yaml",
    "local": "configs/local.yaml",
}


def resolve_config_path() -> str:
    class _Config(Config):
        env = Choice(["prod", "local", "staging"], cast_function=str.lower, default="prod")

    selector = _Config(Env(prefix="APP"))
    return CONFIG_FILES[selector.env]
```

## Where to go next

- Revisit the [API reference](api.md) for detailed signatures and extension points.
- Skim the [Quickstart](quickstart.md) if you want a linear setup guide.
- Explore the `tests/` directory for executable examples that pair with these tutorials.
