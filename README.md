# PKonfig

__P__ stands for __Python__.

[![pypi](https://img.shields.io/pypi/v/pkonfig.svg)](https://pypi.python.org/pypi/pkonfig)
[![downloads](https://img.shields.io/pypi/dm/pkonfig)](https://pepy.tech/project/pkonfig)
[![versions](https://img.shields.io/pypi/pyversions/pkonfig.svg)](https://github.com/ngladkikh/pkonfig)
[![license](https://img.shields.io/github/license/ngladkikh/pkonfig.svg)](https://github.com/ngladkikh/pkonfig/blob/master/LICENSE)

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

## Installation

To install basic PKonfig without YAML and TOML support run:

```bash
pip install pkonfig
```

YAML files parsing is handled with [PyYaml](https://pypi.org/project/PyYAML/):

```bash
pip install pkonfig[yaml]
```

TOML files handled with help of [Tomli](https://pypi.org/project/tomli/):

```bash
pip install pkonfig[toml]
```

And if both TOML and YAML is needed:

```bash
pip install pkonfig[toml,yaml]
```

For production no __.env__ files are needed but propper environment variables should be set.
In case some of required variables missing __KeyError__ exception raised while __AppConfig__
instantiation.

## Quickstart

The most basic usage example when environment variables are used for production
environment and DotEnv files are used for local development.

Create __config__ module __config.py__:

```python
from collections import ChainMap
from pkonfig import Config, EmbeddedConfig, Env, DotEnv, LogLevel, Choice


class PG(EmbeddedConfig):
  host = "localhost"
  port = 5432
  user: str
  password: str

  
class AppConfig(Config):
    db = PG()
    log_level = LogLevel("INFO")
    env = Choice(["local", "prod", "test"], default="prod")


storage = ChainMap(DotEnv(".env", missing_ok=True), Env())
config = AppConfig(storage)
```

For local development create DotEnv file in root app folder __.env__:

```dotenv
APP_DB_HOST=localhost
APP_DB_USER=postgres
APP_DB_PASSWORD=postgres
APP_ENV=local
APP_LOG_LEVEL=debug
```

Then elsewhere in app you could run:

```python
from config import config

print(config.env)           # local
print(config.log_level)     # 20
print(config.db.host)       # localhost
print(config.db.port)       # 5432
print(config.db.user)       # postgres
print(config.db.password)   # postgres
```

## Usage

### Config sources

__PKonfig__ implements several config sources out of the box.
All config sources implement `Mapping` protocol and default values could be set up during initialization.

#### Environment variables

The most common way to configure application is environment variables.
To parse environment variables and store values in multilevel structure class `Env` could be used.
Common pattern is naming variables with multiple words describing the exact purpose 
more precise: __PG_HOST__, __PG_PORT__ and __REDIS_HOST__, __REDIS_PORT__ could be treated as two groups:

- PG
  - HOST
  - PORT
- REDIS
  - HOST
  - PORT

PKonfig respects this convention so that `Env` has two optional arguments:

- `delimiter` string that will be used to split configuration levels taken from keys;
- `prefix` string that is used to identify keys that are related to the given app and omit everything else.

```python
from os import environ
from pkonfig import Env


environ["APP_OUTER"] = "foo"
environ["APP_INNER_KEY"] = "baz"
environ["NOPE"] = "qwe"

source = Env(delimiter="_", prefix="APP", some_key="some")

print(source["outer"])          # foo
print(source["inner"]["key"])   # baz
print(source["nope"])           # raises KeyError
```

`Env` ignores key cases and ignores all keys starting not from __prefix__.

#### DotEnv

In the same manner as environment variables DotEnv files could be used.
`DotEnv` requires file name as a string or a path and also accepts `delimiter` and `prefix` optional arguments.
`missing_ok` argument defines whether `DotEnv` raises exception when given file not found.
When file not found and `missing_ok` is set `DotEnv` contains empty dictionary.

```python
from pkonfig import DotEnv


config_source = DotEnv("test.env", delimiter="_", prefix="APP", missing_ok=True)
```

#### Ini

__INI__ files are quite common and class `Ini` 
is build on top of [`configparser.ConfigParser`](https://docs.python.org/3/library/configparser.html):

```python
from pkonfig import Ini

storage = Ini("config.ini", missing_ok=False)
print(storage["bitbucket.org"]["User"])  # hg
print(storage["bitbucket.org"]["ServerAliveInterval"])  # 45
```

In case when __config.ini__:

```ini
[DEFAULT]
ServerAliveInterval = 45

[bitbucket.org]
User = hg
```

`Ini` also accepts `missing_ok` argument to ignore missing file.
Most of `ConfigParser` arguments are also accepted to modify parser behaviour.

#### Json

`Json` class uses `json.load` to read given JSON file and respects `missing_ok` argument:

```python
from pkonfig import Json


storage = Json("config.json", missing_ok=False)
```

#### Yaml

To parse YAML files [PyYaml](https://pyyaml.org/wiki/PyYAMLDocumentation) could be used wrapped with `Yaml` class:

```python
from pkonfig import Yaml

storage = Yaml("config.yaml", missing_ok=False)
```

#### Toml

TOML files are parsed with [tomli](https://pypi.org/project/tomli/) wrapped with `Toml` helper class:

```python
from pkonfig import Toml


storage = Toml("config.toml", missing_ok=False)
```

### Source order

Any source for `BaseConfig` should implement `Mapper` protocol.
So it is easy to implement custom or combine existing implementations.
Recommended way to combine multiple sources of configs is `ChainMap`:

```python
from collections import ChainMap
from pkonfig import Env, DotEnv, Yaml


config_source = ChainMap(
    DotEnv("test.env", missing_ok=True),
    Env(),
    Yaml("base_config.yaml")
)
```

In this example we created `ChainMap` that looks for key until finds one in the given mappers sequence.
The first one source for configs is **test.env** file that might not exist and could be used for local development only.
Environment variables are used as the second one config source.
Dotenv file will be preferred source in this example.
The last one source is **base_config.yaml** that should exist or `FileNotFoundError` exception raised.

You can customize source order in this way or even create your own logic implementing
`Mapper` protocol.

### Config

To implement application config class user should inherit from `pkonfig.config.Config` class and define
required fields:

```python
from pkonfig import Config


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
from pkonfig import Config, EmbeddedConfig


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

### Multilevel Config

Grouping might be useful when there are lots of config parameters.
To achieve this `EmbeddedConfig` class should be inherited:

```python
from pkonfig import DotEnv, Config, EmbeddedConfig


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

print(config.pg.host)       # db_host
print(config.pg.port)       # 6432
print(config.redis.host)    # redis
```

__.env__ content:
```dotenv
APP__PG__HOST=db_host
APP__PG__PORT=6432
APP__REDIS__HOST=redis
```
In this example we customized delimiter with two underscores, default is '**_**'.

### Aliases

All __Config__ fields accept __alias__ argument. 
When storage class searches for config attribute in its source either attribute
name is used or alias when it is set.

__config.py__:
```python
from pkonfig import DotEnv, EmbeddedConfig, Config, Int, Str


class HostConfig(EmbeddedConfig):
    host: str
    port: int
    user: str
    password = Str(alias="pass")


class AppConfig(Config):
    pg = HostConfig(alias="db")
    foo_baz = Int(alias="my_alias")


config = AppConfig(DotEnv(".env", delimiter="__"))
```

__.env__ content:

```dotenv
APP__DB__HOST=db_host
APP__DB__PORT=6432
APP__DB__PASS=password
APP__DB__USER=postgres
APP__MY_ALIAS=123
```

In this example storage will seek in dotenv file parameters named by given alias.
Elsewhere in an app:

```python
from config import config


print(config.foo_baz)       # 123
print(config.pg.password)   # password
```

### PKonfig fields

All simple Python data types are implemented in field types: `Bool`, `Int`, `Float`, `Str`, `Byte`, `ByteArray`.
All fields with known type converted to descriptors during class creation.
Fields in `Config` classes may be defined in several ways:

#### Using types:
```python
from pathlib import Path
from pkonfig import Config


class AppConfig(Config):
    foo: str
    baz: int
    flag: bool
    file: Path
```

#### Using default values:

```python
from pathlib import Path
from pkonfig import Config


class AppConfig(Config):
    foo = "some"
    baz = 1
    flag = False
    file = Path("some.text")
```

Given values will be used as default values.

#### Using PKonfig fields directly

```python
from pkonfig import Config, PathField, Str, Int, Bool


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
from pkonfig import Config, Int


class AppConfig(Config):
    attr = Int(no_cache=True)
```

In given example `attr` will do type casting and validation every time this attribute is accessed.

#### Default values

If value is not set in config source user can use default value.
`None` could be used as default value:

```python
from pkonfig import Config, Int, Str


class AppConfig(Config):
    int_attr = Int(None)
    str_attr = Str(None)

config = AppConfig({})
print(config.str_attr)    # None
print(config.int_attr)    # None
```

When `None` is default value field is treated as nullable.

#### Field nullability

To handle type casting and validation fields should not be nullable.
In case `None` is a valid value and should be used without casting and validation
option `nullable` could be set:

```python
from pkonfig import Int, Config


class AppConfig(Config):
    int_attr = Int(nullable=True)

config = AppConfig(dict(int_attr=None))
print(config.int_attr)    # None
```

In this example `None` comes from storage and type casting is omitted.

### Custom descriptor or property

```python
from pkonfig import Config


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
from pkonfig import Config, Int


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
from pkonfig import Field

class ListOfStrings(Field):
    def cast(self, value: str) -> List[str]:
        return value.split(",")
```

### Available fields

Builtin Python types has appropriate `Field` types:

- bool -> `Bool`
- int -> `Int`
- float -> `Float`
- Decimal -> `DecimalField`
- str -> `Str`
- bytes -> `Byte`
- bytearray -> `ByteArray`

The only reason to use this types directly is customising field nullability and cache policy.

#### PathField

Basic path type that is parental for other two types and is used when you define field using `pathlib.Path`.
This type raises `FileNotFoundError` exception during initialization if given path doesn't exist:

```python
from pkonfig import Config, PathField


class AppConfig(Config):
    mandatory_existing_path = PathField()
    optional_path = PathField(missing_ok=True)
```

In given example field `optional_path` may not exist during initialization.

##### File

`File` inherits `PathField` but also checks whether given path is a file.

#### Folder

`Folder` inherits `PathField` and does checking whether given path is a folder.

#### EnumField

This field uses custom enum to validate input and cast it to given `Enum`:

```python
from enum import Enum
from pkonfig import Config, EnumField


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
from pkonfig import Config, LogLevel


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

`Choice` field validates that config value is a member of the given sequence and also does optional type casting:

```python
from pkonfig import Config, Choice


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
This mapping is used by default:
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
from pkonfig import Config, DefaultMapper, DecimalField


class AppConfig(Config):
    _mapper = DefaultMapper({float: DecimalField})
    foo: float

config = AppConfig(dict(foo=1/3))
assert isinstance(config.foo, Decimal)  # True
```

### Per-environment config files

When your app is configured with different configuration files 
and each file is used only in an appropriate environment you can create a function
to find which file should be used:

```python
from pkonfig import Env, Yaml, Config, Choice


CONFIG_FILES = {
    "prod": "configs/prod.yaml",
    "staging": "configs/staging.yaml",
    "local": "configs/local.yaml",
}


def get_config_file():
    class _Config(Config):
        env = Choice(
          ["prod", "local", "staging"], 
          cast_function=str.lower,
          default="prod"
        )
    
    _config = _Config(Env())
    return CONFIG_FILES[_config.env]
```

__get_config_file__ uses environment variables and predefined config files pathes
to check whether __APP_ENV__ var is set, validate this variable and return appropriate
config file name.
Then actual application configuration:

```python
from collections import ChainMap
from pkonfig import Env, Yaml, Config, Choice


CONFIG_FILES = {
    "prod": "configs/prod.yaml",
    "staging": "configs/staging.yaml",
    "local": "configs/local.yaml",
}


def get_config_file():
    class _Config(Config):
        env = Choice(
          ["prod", "local", "staging"], 
          cast_function=str.lower,
          default="prod"
        )
    
    _config = _Config(Env())
    return CONFIG_FILES[_config.env]


class AppConfig(Config):
    env = Choice(
        ["prod", "local", "staging"], 
        cast_function=str.lower,
        default="prod"
    )
    ...

storage = ChainMap(
  Env(),
  Yaml(get_config_file()),
)
config = AppConfig(storage)
```
