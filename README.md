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

### Config

To implement application config class user should inherit from `pkonfig.config.Config` class and define
required fields:

```python
from pkonfig.config import Config


class AppConfig(Config):
    foo: float
    baz: int


storage = {"foo": "0.33", "baz": 1}
config = AppConfig(storage)

print(config.foo)   # 0.33
print(config.baz)   # 1
```

To build more granular config structure `EmbeddedConfig` class is used:

```python
from pkonfig.config import Config, EmbeddedConfig


class Inner(EmbeddedConfig):
    key: str


class AppConfig(Config):
    inner = Inner()
    foo: float
    baz: int


storage = {
    "foo": "0.33", 
    "baz": 1, 
    "inner": {"key": "value"}
}
config = AppConfig(storage)

print(config.inner.key)   # value
```

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

Previous example might be simplified using `alias` field attribute 
that is used to get raw values from given storage:

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

### PKonfig fields

All simple Python data types are implemented in field types: `Bool`, `Int`, `Float`, `Str`, `Byte`, `ByteArray`.
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

Given values will be used as default values.

#### Using PKonfig fields directly

```python
from pkonfig.config import Config
from pkonfig.fields import PathField, Str, Int, Bool


class AppConfig(Config):
    foo = Str()
    baz = Int()
    flag = Bool()
    file = PathField()
```

#### Caching

All __PKonfig__ field types are Python descriptors that are responsible for type casting and data validation.
In most cases there is no need to do this job every time the value is accessed.
To avoid undesirable calculations caching is used.
So that type casting and validation is done only once 
during `Config` object initialization.
In case when configuration may change during application lifecycle user may disable this behaviour:

```python
from pkonfig.fields import Int
from pkonfig.config import Config


class AppConfig(Config):
    attr = Int(no_cache=True)
```

In given example `attr` will do type casting and validation every time this attribute is accessed.

#### Default values

If value is not set in config source user can use default value.
`None` is also to be valid default type:

```python
from pkonfig.fields import Int, Str
from pkonfig.config import Config


class AppConfig(Config):
    int_attr = Int(1)
    none_default_attribute = Str(None)

config = AppConfig({})
print(config.none_default_attribute)    # None
```

### Implement custom descriptor or property

```python
from pkonfig.config import Config


class AppConfig(Config):
    flag = True
    baz = "test"
    
    @property
    def value(self):
        return self.flag and self.baz == "test" 


config = AppConfig({})
print(config.value)  # True
```

### Custom field types

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

### Available fields

#### PathField

Basic path type that is parental for other two types and is used when you define field using `pathlib.Path`.
This type raises `FileNotFoundError` exception during initialization if given path doesn't exist by default:

```python
from pkonfig.fields import PathField
from pkonfig.config import Config


class AppConfig(Config):
    mandatory_existing_path = PathField()
    optional_path = PathField(missing_ok=True)
```

In given example field `optional_path` may not exist during initialization.

##### File

`File` inherits `PathField` but also checks whether given path is a file.

#### Folder

`Folder` inherits `PathField` and does checking whether given path is a folder.

### EnumField

This field uses custom enum to validate input and cast it to given `Enum`:

```python
from enum import Enum
from pkonfig.fields import EnumField
from pkonfig.config import Config


class UserType(Enum):
    guest = 1
    user = 2
    admin = 3


class AppConfig(Config):
    user_type = EnumField(UserType)


config = AppConfig({"user_type": "admin"})
print(config.user_type is UserType.admin)  # True
```

#### LogLevel

`LogLevel` field is useful to define `logging` level through configs.
`LogLevel` accepts strings that define log level and casts 
that string to `logging` level integer value:

```python
import logging
from pkonfig.fields import LogLevel
from pkonfig.config import Config


class AppConfig(Config):
    some_level = LogLevel()
    another_level = LogLevel()


config = AppConfig(
    {
        "some_level": "info",
        "another_level": "Debug",
    }
)

print(config.some_level)        # 20
print(config.another_level)     # 10

print(config.another_level is logging.DEBUG)     # True
```

#### Choice

`Choice` field validates that config value is one of given and also does optional type casting:

```python
from pkonfig.fields import Choice
from pkonfig.config import Config


class AppConfig(Config):
    one_of_attr = Choice([10, 100], cast_function=int)


config = AppConfig({"one_of_attr": "10"})
print(config.one_of_attr == 10)  # True

config = AppConfig({"one_of_attr": "2"})    # raises TypeError exception
```

When `cast_function` is not given raw values from storage are used.

### Types to Fields mapping

All fields for `BaseConfig` children classes are converted to descriptors internally.
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
