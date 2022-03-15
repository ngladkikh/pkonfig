# PKonfig

__P__ stends for __Python__.

## Prerequisites

- Pythonic configuration management helpers.
- Multiple sources of configs (environment variables, dotenv files, YAML, JSON, TOML, INI)
with agile order configuration.
- Configs validation mechanics based on type hints or user defined.
- Minimal external dependencies.
- Follow [Fail-fast](https://en.wikipedia.org/wiki/Fail-fast) principle.
- Autocomplete in modern IDEs.

## Quickstart

## Features

- User defined config source order.
- Multilevel configs for environment variables and dotenv config sources.
- Custom aliases for fields or groups of configs.
- Configs type casting
- Config values validation based on type and/or value.
- High performance.
- Extendable API.

### Source order

```python
from collections import ChainMap
from pkonfig.storage import Env, DotEnv, Yaml


config_source = ChainMap(
    DotEnv("test.env", missing_ok=True),
    Env(),
    Yaml("base_config.yaml")
)
```

In this example we created `ChainMap` that looks for key until finds it in given mappers.
Here the first one source for configs is **test.env** file that might not exist.
The second one source of configs will be environment variables.
So in this example dotenv file will be preferred over environment.
The last one source is **base_config.yaml** that should exist otherwise `FileNotFoundError` will be raised.

You can customize source order in this way or even create your own logic implementing
`MutableMapping` interface.

### Environment variables naming conventions

Storing configs in environment variables is the easiest and most common way to configurate your app.
But when there are lots of parameters it is quite complicated to maintain all of them in a plain structure and some
grouping might be useful. Common pattern is naming variables with multiple words describing the exact purpose 
more precise: __PG_HOST__ and __REDIS_HOST__ as an example. 
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
```

__.env__ content:
```dotenv
APP__PG__HOST=localhost
APP__PG__PORT=6432
APP__REDIS__HOST=localhost
```
In this example we customized delimiter with two underscores, default is '**_**'.
We also can customize prefix parameter so that our app uses variables starting from __prefix__ only.
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
from decimal import Decimal
from pkonfig.base import Field

class DecimalField(Field):
    def cast(self, value) -> Decimal:
        return Decimal(float(value))
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
}
```

When field type is not found in this mapper it is ignored and won't be taken from storage source while resolving.

User can customize this behaviour by defining type mapper class and setting it as resolver:

```python
from typing import Type, Dict
from pkonfig.base import TypeMapper, Field, NOT_SET
from pkonfig.fields import Bool, Int, Str, Byte, ByteArray, Float
from pkonfig.config import BaseOuterConfig


class StrictMapper(TypeMapper):
    mapper: Dict[Type, Type[Field]] = {
        bool: Bool,
        int: Int,
        float: Float,
        str: Str,
        bytes: Byte,
        bytearray: ByteArray,
    }

    def descriptor(self, type_: Type, value=NOT_SET) -> Field:
        return self.mapper[type_](value)


class AppConfig(BaseOuterConfig):
    Mapper = StrictMapper()
    
    foo = "baz"
```

In this example `StrictMapper` raises exception when field type is not found.

Another option is to modify default mapper directly:


```python
from pkonfig.config import Config
from decimal import Decimal
from pkonfig.base import Field

class DecimalField(Field):
    def cast(self, value) -> Decimal:
        return Decimal(float(value))

Config.Mapper

class AppConfig(Config):
    foo = "baz"
```
