# PKonfig

__P__ stends for __Python__.

## Prerequisites

- Pythonic configuration management helpers.
- Multiple sources of configs (environment variables, dotenv files, YAML, JSON, TOML, INI)
with agile order configuration.
- Configs validation mechanics based on type hints or user defined classes.
- Minimal external dependencies.
- Follow [Fail-fast](https://en.wikipedia.org/wiki/Fail-fast) principle.
- Autocomplete in modern IDEs.

## Features

- User defined config source order.
- Multilevel configs for environment variables and dotenv config sources.
- Custom aliases for fields or groups of configs.
- Configs type casting
- Config values validation based on type and/or value.
- High performance.
- Extendable API.

## Quickstart

### Source order

Any source for `BaseConfig` should implement `Mapper` protocol.
So it is easy to implement custom or combine existing implementations.
Recommended way to combine multiple sources of configs is using `ChainMap`:

```python
from collections import ChainMap
from pkonfig.storage import Env, DotEnv, Yaml


config_source = ChainMap(
    DotEnv("test.env", missing_ok=True),
    Env(),
    Yaml("base_config.yaml")
)
```

In this example we created `ChainMap` that looks for key until finds one in the given mappers sequence.
The first one source for configs is **test.env** file that might not exist and cpuld be used for local development only.
Environment variables are used as the second one config source.
Dotenv file will be preferred source in this example.
The last one source is **base_config.yaml** that should exist or `FileNotFoundError` exception raised.

You can customize source order in this way or even create your own logic implementing
`Mapper` protocol.

### Environment variables naming conventions

Storing configs in environment variables is the easiest and most common way to configurate your app.
But when there are lots of parameters it is quite complicated to maintain all of them in a plain structure and some
grouping might be useful. Common pattern is naming variables with multiple words describing the exact purpose 
more precise: __PG_HOST__, __PG_PORT__ and __REDIS_HOST__, __REDIS_PORT__ as an example. 
PKonfig respects this convention.

```python
from pkonfig.storage import DotEnv
from pkonfig.config import Config, EmbeddedConfig


class PgConfig(EmbeddedConfig):
    host: str
    port: int = 5432


class RedisConfig(EmbeddedConfig):
    host: str
    port: int = 6379


class AppConfig(Config):
    pg = PgConfig()
    redis = RedisConfig()


config = AppConfig(
    DotEnv(".env", delimiter="__", prefix="APP")
)

print(config.pg.host)   # 'db_host'
```

__.env__ content:
```dotenv
APP__PG__HOST=db_host
APP__PG__PORT=6432
APP__REDIS__HOST=redis
```
In this example we customized delimiter with two underscores, default is '**_**'.
Prefix parameter could be also customized so that our app uses variables starting from __prefix__ only.
Prefix is `APP` by default.

### Aliases

Previous example might be simplified:
```python
from pkonfig.storage import DotEnv
from pkonfig.config import Config, EmbeddedConfig
from pkonfig.fields import Str


class HostConfig(EmbeddedConfig):
    host: str
    port: int


class AppConfig(Config):
    pg = HostConfig(alias="pg")
    redis = HostConfig(alias="redis")
    foo = Str(alias="baz")


config = AppConfig(
    DotEnv(".env", delimiter="__", prefix="APP")
)
```

In this example storage will seek in dotenv file parameters named by given alias.
Also field `AppConfig.foo` will use value taken by key __baz__ rather than __foo__.

### Fields definition and type casting

Fields in `Config` classes may be defined in several ways:

#### Using types:
```python
from pathlib import Path
from pkonfig.config import Config


class AppConfig(Config):
    foo: str
    baz: int
    flag: bool
    file: Path
```

#### Using default values:

```python
from pathlib import Path
from pkonfig.config import Config


class AppConfig(Config):
    foo = "some"
    baz = 1
    flag = False
    file = Path("some.text")
```

#### Using pkonfig fields directly

```python
from pkonfig.config import Config
from pkonfig.fields import PathField, Str, Int, Bool


class AppConfig(Config):
    foo = Str()
    baz = Int()
    flag = Bool()
    file = PathField()
```

#### Implement custom descriptor or property

```python
from pkonfig.config import Config


class AppConfig(Config):
    flag = True
    baz = "test"
    
    @property
    def value(self):
        return self.flag and self.baz == "prod" 
```

#### Custom field types

User can customize how field validation and casting is done.
The recommended way is to implement `validate` method:

```python
from pkonfig.config import Config
from pkonfig.fields import Int


class OnlyPositive(Int):
    def validate(self, value):
        if value < 0:
            raise ValueError("Only positive values accepted")


class AppConfig(Config):
    positive = OnlyPositive()
```

Custom type casting is also available.
To achieve this user should inherit abstract class `Field` and implement method `cast`:

```python
from typing import List
from pkonfig.base import Field

class ListOfStrings(Field):
    def cast(self, value: str) -> List[str]:
        return value.split(",")
```

### Types to Fields mapping

All fields for `Config` children classes are converted to descriptors internally.
Class `pkonfig.config.DefaultMapper` defines how field types will be replaced with descriptors.
This mapper is used as base:
```
{
    bool: Bool,
    int: Int,
    float: Float,
    str: Str,
    bytes: Byte,
    bytearray: ByteArray,
    Path: PathField,
    Decimal: DecimalField,
}
```

When field type is not found in this mapper it is ignored and won't be taken from storage source while resolving.

User can modify default mapper giving dictionary of types and appropriate fields:

```python
from decimal import Decimal
from pkonfig.config import Config, DefaultMapper
from pkonfig.fields import DecimalField


class AppConfig(Config):
    _mapper = DefaultMapper({float: DecimalField})
    foo: float

config = AppConfig(dict(foo=1/3))
assert isinstance(config.foo, Decimal)  # True
```
