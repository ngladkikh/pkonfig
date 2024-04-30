# PKonfig

__P__ stands for __Python__.

[![pypi](https://img.shields.io/pypi/v/pkonfig.svg)](https://pypi.python.org/pypi/pkonfig)
[![downloads](https://img.shields.io/pypi/dm/pkonfig)](https://pepy.tech/project/pkonfig)
[![versions](https://img.shields.io/pypi/pyversions/pkonfig.svg)](https://github.com/ngladkikh/pkonfig)
[![license](https://img.shields.io/github/license/ngladkikh/pkonfig.svg)](https://github.com/ngladkikh/pkonfig/blob/master/LICENSE)
[![Type Checked with Mypy](https://img.shields.io/badge/Type%20Check-Mypy-brightgreen)](https://mypy.readthedocs.io/en/stable/)
[![Code Quality - Pylint](https://img.shields.io/badge/Code%20Quality-Pylint-blue)](https://www.pylint.org/)
[![Code Style - Black](https://img.shields.io/badge/Code%20Style-Black-black)](https://github.com/psf/black)
[![Code Style - isort](https://img.shields.io/badge/Code%20Style-isort-%231674b1)](https://pycqa.github.io/isort/)
[![codecov](https://codecov.io/github/ngladkikh/pkonfig/branch/main/graph/badge.svg?token=VDRSB1XUFH)](https://codecov.io/github/ngladkikh/pkonfig)

## Prerequisites

- Pythonic configuration management helpers.
- Multiple sources of configs (environment variables, dotenv files, YAML, JSON, TOML, INI)
  with agile order configuration.
- Configs validation mechanics based on type hints or user defined classes.
- Minimal external dependencies.
- Follow [Fail-fast](https://en.wikipedia.org/wiki/Fail-fast) principle.
- Autocomplete in modern IDEs.

## Features

- User defined config source order: Define the order in which PKonfig looks for configuration values.
- Multilevel configs for environment variables and dotenv config sources: Allows for more granular control over configuration values.
- Custom aliases for fields or groups of configs: Create custom aliases for configuration values to make them easier to reference in code.
- Configs type casting: Automatically cast configuration values to the correct data type.
- Config values validation based on type and/or value: Validate configuration values to ensure they meet specific requirements.
- High performance: Designed to be fast and efficient.
- Extendable API: Easily extend PKonfig to meet your specific needs.

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

For production no __.env__ files are needed but proper environment variables should be set.
In case some of required variables missing __ConfigValueNotFoundError__ exception raised while __AppConfig__
instantiation.

## Quickstart

The Config class is a Pythonic configuration management helper designed
to provide a simple way of managing multiple sources of configuration values in your application.
The most basic usage example when environment variables are used for production
environment and DotEnv files are used for local development.

Create __config__ module __config.py__:

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

For local development create DotEnv file in root app folder __.env__:

```dotenv
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

## Usage

### Config sources

__PKonfig__ implements several config sources out of the box.
Use `DictStorage` if some defaults should be stored from code rather than from field default values:

```python
from pkonfig import Config, Str, DictStorage


class AppConfig(Config):
    foo: str = Str()    # foo has no default value and raise an exception if value not found in storage


CONFIG = AppConfig(DictStorage(foo="baz"))
print(CONFIG.foo)   # 'baz'
```

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
from pkonfig.storage import Env

environ["APP_OUTER"] = "foo"
environ["APP_INNER_KEY"] = "baz"
environ["NOPE"] = "qwe"

source = Env(delimiter="_", prefix="APP")

print(source[("outer",)])  # foo
print(source[("inner", "key")])  # baz
print(source[("nope",)])  # raises KeyError
```

`Env` ignores key cases and ignores all keys starting not from __prefix__.
To change this behaviour set __prefix__ to `None` or an empty string.
In this case you will get all key value pairs:

```python
from os import environ
from pkonfig import Env

environ["NOPE"] = "qwe"

source = Env(prefix=None)

print(source[("nope",)])   # qwe
```

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
is build on top of [`configparser.ConfigParser`](https://docs.python.org/3/library/configparser.html).

**config.ini** file example:

```ini
[DEFAULT]
ServerAliveInterval = 45

[bitbucket.org]
User = hg
```

Then in Python code:

```python
from pkonfig.storage import Ini

storage = Ini("config.ini", missing_ok=False)
print(storage[("bitbucket.org", "User")])  # hg
print(storage[("bitbucket.org", "ServerAliveInterval")])  # 45
```

`Ini` also accepts `missing_ok` argument to ignore missing file.
Most of `ConfigParser` arguments are also accepted to modify parser behaviour.

#### Json

`Json` class uses `json.load` to read given JSON file and respects `missing_ok` argument:

```python
from pkonfig.storage import Json

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
from pkonfig import Config, Env, Yaml, DotEnv, Str


class AppConfig(Config):
    foo: str = Str()


config = AppConfig(
    DotEnv("test.env", missing_ok=True),
    Env(),
    Yaml("base_config.yaml"),
)
```

In this example we created `AppConfig` that looks for key until finds one in the given mappers sequence.
The first one source for configs is **test.env** file that might not exist and could be used for local development only.
Then environment variables are used as the second one config source.
The last one is **base_config.yaml** that should exist or `FileNotFoundError` exception raised.
You can customize source order.

### Config

To implement application config class user should inherit from `pkonfig.config.Config` class and define
required fields:

```python
from pkonfig import Config, Float, Int, DictStorage


class AppConfig(Config):
    foo: float = Float()
    baz: int = Int()


config = AppConfig(DictStorage(**{"foo": "0.33", "baz": 1}))

print(config.foo)   # 0.33
print(config.baz)   # 1
```

To build more granular config structure:

```python
from pkonfig import Config, DictStorage, Float, Int, Str


class Inner(Config):
    key: str = Str()


class AppConfig(Config):
    inner = Inner()
    foo: float = Float()
    baz: int = Int()


storage = DictStorage(
    **{
        "foo": "0.33",
        "baz": 1,
        "inner": {"key": "value"}
    }
)
config = AppConfig(storage)

print(config.inner.key)   # value
```

### Multilevel Config

Grouping might be useful when there are lots of config parameters.
To achieve this `Config` class should be inherited like:

```python
from pkonfig import Config, DotEnv, Str, Int


class PgConfig(Config):
    host: str = Str("localhost")
    port: int = Int(5432)


class RedisConfig(Config):
    host: str = Str("localhost")
    port: int = Int(6379)


class AppConfig(Config):
    pg = PgConfig()
    redis = RedisConfig()


config = AppConfig(
    DotEnv(".env", delimiter="__", prefix="APP")
)

print(config.pg.host)  # db_host
print(config.pg.port)  # 6432
print(config.redis.host)  # redis
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
from pkonfig import Config, Int, Str, DotEnv


class HostConfig(Config):
    host: str = Str("localhost")
    port: int = Int(5432)
    user: str = Str("user")
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
Elsewhere in the app:

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

#### Caching

All __PKonfig__ field types are Python descriptors that are responsible for type casting and data validation.
In most cases there is no need to do this job every time the value is accessed.
To avoid undesirable calculations caching is used.
So that type casting and validation is done only once during `Config` object initialization.

#### Default values

If value is not set in config source user can use default value.
`None` could be used as default value:

```python
from pkonfig import Config, Int, Str, DictStorage


class AppConfig(Config):
    int_attr = Int(None)
    str_attr = Str(None)

config = AppConfig(DictStorage())
print(config.str_attr)    # None
print(config.int_attr)    # None
```

When `None` is default value the field is treated as nullable.

#### Field nullability

To handle type casting and validation fields should not be nullable.
In case `None` is a valid value and should be used without casting and validation
option `nullable` could be set:

```python
from pkonfig import Int, Config, DictStorage


class AppConfig(Config):
    int_attr = Int(nullable=True)

config = AppConfig(DictStorage(int_attr=None))
print(config.int_attr)    # None
```

In this example when `None` comes from storage type casting and validation is omitted.

By default, fields are treated as not nullable:

```python
from pkonfig import Int, Config, DictStorage


class AppConfig(Config):
    int_attr = Int(default=1)

config = AppConfig(DictStorage(int_attr=None))  # ValueError("Not nullable") is raised here
```

### Custom descriptor or property

```python
from pkonfig import Config, Bool, DictStorage, Str


class AppConfig(Config):
    flag: bool = Bool(True)
    baz: str = Str("test")

    @property
    def value(self):
        return self.flag and self.baz == "test"


config = AppConfig(DictStorage())
print(config.value)  # True
```

### Custom field types

User can customize how field validation and casting is done.
The recommended way is to implement `validate` method:

```python
from pkonfig import Config, Int


class OnlyPositive(Int):
    def validate(self, value) -> None:
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
from pkonfig import Config, EnumField, DictStorage, Int


class UserType(Enum):
    guest = Int(1)
    user = Int(2)
    admin = Int(3)


class AppConfig(Config):
    user_type = EnumField(UserType)


config = AppConfig(DictStorage(user_type="admin"))
print(config.user_type is UserType.admin)  # True
```

#### LogLevel

`LogLevel` field is useful to define `logging` level through configs.
`LogLevel` accepts strings that define log level and casts
that string to `logging` level integer value:

```python
import logging
from pkonfig import Config, LogLevel, DictStorage


class AppConfig(Config):
    some_level = LogLevel()
    another_level = LogLevel()


config = AppConfig(
    DictStorage(
        some_level="info",
        another_level="Debug",
    )
)

print(config.some_level)        # 20
print(config.another_level)     # 10

print(config.another_level is logging.DEBUG)     # True
```

#### Choice

`Choice` field validates that config value is a member of the given sequence and also does optional type casting:

```python
from pkonfig import Config, Choice, DictStorage


class AppConfig(Config):
    one_of_attr = Choice([10, 100], cast_function=int)


config = AppConfig(DictStorage(one_of_attr="10"))
print(config.one_of_attr == 10)  # True

config = AppConfig(DictStorage(one_of_attr="2"))    # raises TypeError exception
```

When `cast_function` is not given raw values from storage are used.

#### DebugFlag

`DebugFlag` helps to set widely used __debug__ option.
`DebugFlag` ignores value case and treats __'true'__ string as `True` and any other value as `False`:

```python
from pkonfig import Config, Bool, DictStorage


class AppConfig(Config):
    lower_case = Bool()
    upper_case = Bool()
    random_string = Bool()


config = AppConfig(
    DictStorage(
        lower_case="true",
        upper_case="TRUE",
        random_string="foo",
    )
)
print(config.lower_case)        # True
print(config.upper_case)        # True
print(config.random_string)     # False
```

### Per-environment config files

When your app is configured with different configuration files
and each file is used only in an appropriate environment you can create a function
to find which file should be used:

```python
from pkonfig import Env, Config, Choice


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

__get_config_file__ uses environment variables and predefined config files paths
to check whether __APP_ENV__ var is set, validate this variable and return appropriate
config file name.
Then actual application configuration:

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


class AppConfig(Config):
    env = Choice(
        ["prod", "local", "staging"],
        cast_function=str.lower,
        default="prod"
    )
    ...


config = AppConfig(Env(), Yaml(get_config_file()))
```

### Fail fast

Very often it is helpful to check app configs existence and validate values before the app does something.
To achieve this `Config` class runs `check` as the last step in it's `__init__` method.
`check` recursively gets from storage and verifies all defined config attributes.
When this behaviour is not desirable for some reason user can set flag `fail_fast` to `False`:

```python
from pkonfig import Config, DotEnv, ConfigValueNotFoundError


class AppConfig(Config):
    foo: str


try:
    config = AppConfig(DotEnv(".env"))
except ConfigValueNotFoundError as exc:
    print(exc)  # config.foo not found

config = AppConfig(DotEnv(".env"), fail_fast=False) # No error raised
config.foo  # This line actually causes `config.foo not found` exception
```