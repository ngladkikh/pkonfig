
# API Reference

This reference provides a practical, browsable overview of PKonfig’s public API with direct links, short summaries, and detailed signatures. See Quickstart for a guided introduction and examples.

- Core configuration container (`Config`) and validation workflow.
- Typed fields and how they convert raw source values.
- Storage backends for merging environment variables and config files.
- Error types you can catch in your application.

:::{seealso}
[Tutorials](tutorials.md) — deep dives and step-by-step guides that expand on the API overview.
:::

```{eval-rst}
.. py:module:: pkonfig
```

## Core

### Config

High-level configuration container. Subclass it and declare Field descriptors.

**Key takeaways**
- Pass one or more storage backends in priority order (`Env`, `Yaml`, etc.).
- Use `alias="..."` to namespace nested configs when composing large trees.
- Leave `fail_fast=True` in production to surface validation errors during start-up.

:::{tip}
Call `cfg.check()` if you instantiate a config with `fail_fast=False` and later want to validate all fields eagerly.
:::

#### Nested configs

Nest `Config` subclasses as class attributes to create structured groups. Aliases cascade automatically so nested keys match the parent hierarchy when resolving values.

```{eval-rst}
.. autoclass:: pkonfig.config.Config
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
```

Usage example

```python
from pkonfig import fields as f
from pkonfig import storage
from pkonfig.config import Config

class Database(Config):
    host = f.Str(default="localhost")
    port = f.Int(default=5432)

class App(Config):
    debug = f.Bool(default=False)
    db = Database(alias="db")

cfg = App(storage.Env(prefix="APP"))
print(cfg.debug, cfg.db.port)
```

### Errors

Common exceptions raised by PKonfig.

`ConfigError`
: Base class for all configuration issues. Catch this if you want a single handler for every PKonfig error.

`ConfigValueNotFoundError`
: Raised when a required key is missing across every storage you provided.

`ConfigTypeError`
: Raised when a value exists but cannot be coerced into the field’s declared type.

```{eval-rst}
.. automodule:: pkonfig.errors
   :members:
   :undoc-members:
   :show-inheritance:
```

## Fields

Field descriptors define types, casting, and validation for config values.

```{eval-rst}
.. py:module:: pkonfig.fields
```

`Field`
: Base descriptor with shared validation hooks and metadata.

`Bool`
: Parses truthy strings / integers ("true", "1") into `bool`.

`Int`
: Casts numeric strings into `int`, validating bounds if specified.

`Float`
: Converts values into floating-point numbers.

`DecimalField`
: Preserves precision by returning `Decimal` instances.

`Str`
: Returns raw string values (after optional trimming / defaults).

`Byte`
: Produces immutable `bytes` blobs.

`Bytes`
: Alias to `Byte` for readability.

`ByteArray`
: Produces mutable `bytearray` instances.

`PathField`
: Normalises paths into `pathlib.Path` objects.

`File`
: Validates that the resolved path points to an existing file.

`Folder`
: Validates that the resolved path points to an existing directory.

`EnumField`
: Restricts values to members of a supplied `Enum` type.

`LogLevel`
: Maps strings like "info"/"ERROR" into `logging` level integers.

`Choice`
: Validates membership within a predefined set of allowed values.

`ListField`
: Parse lists from strings or iterables. Useful for values like "a,b,c" or when storages return arrays. Use `cast_function` to convert each element:
```python
from pkonfig import Config, DictStorage
from pkonfig.fields import ListField

class C(Config):
    tags = ListField(cast_function=str)
    ids = ListField(cast_function=int)

cfg = C(DictStorage(tags="a, b, c", ids="1,2,3"))
assert cfg.tags == ["a", "b", "c"]
assert cfg.ids == [1, 2, 3]
```

:::{tip}
All field classes accept `default`, `required`, and optional validator hooks. Compose them to keep environment parsing declarative.
:::

```{eval-rst}
.. autoclass:: pkonfig.fields.Field
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:
```

## Storage backends

```{eval-rst}
.. py:module:: pkonfig.storage
```

Choose one or more storages and pass them to your Config. Leftmost storage has highest priority.

| Storage | Best for | Notes |
| --- | --- | --- |
| `Env` | Runtime overrides via `os.environ` | Optional prefix/delimiter helpers mirror Twelve-Factor style deployment. |
| `DotEnv` | Local developer overrides | Parses `.env` files with comment and prefix handling. |
| `Ini` | Legacy INI configuration | Exposes advanced `configparser` tuning knobs. |
| `Json` | Simple machine-generated settings | Uses `json.load` and preserves nested structures. |
| `Toml` | Modern app configs | Works with `tomllib`/`tomli` automatically. |
| `Yaml` | Verbose hierarchical configs | Uses `yaml.safe_load`; beware implicit type coercion. |

Usage example

```python
from pkonfig import storage
from pkonfig.config import Config
from pkonfig.fields import Str

class Service(Config):
    name = Str(default="api")

cfg = Service(
    storage.Env(prefix="SERVICE"),
    storage.Yaml("settings.yaml", missing_ok=True),
)
print(cfg.name)
```

Base protocol and concrete backends

This page shows a brief index. Follow the links in the overview to get detailed documentation for each storage backend and the BaseStorage protocol.
