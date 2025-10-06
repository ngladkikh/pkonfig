# API Reference

This reference provides a practical, browsable overview of PKonfig’s public API with direct links, short summaries, and detailed signatures. See Quickstart for a guided introduction and examples.


```{eval-rst}
.. py:module:: pkonfig
```

## Core

### Config

High-level configuration container. Subclass it and declare Field descriptors.

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

class App(Config):
    debug = f.Bool(default=False)
    port = f.Int(default=8000)

cfg = App(storage.Env(prefix="APP_"))
print(cfg.debug, cfg.port)
```

### Errors

Common exceptions raised by PKonfig.

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

Built‑in field types

Field — Base config attribute descriptor. See details below.

Bool — Boolean field that accepts typical truthy strings and ints (e.g. 'true', '1').

Int — Integer field.

Float — Floating point number field.

DecimalField — Decimal field stored as Decimal.

Str — String field.

Byte — Bytes field (immutable).

Bytes — Alias for Byte.

ByteArray — Mutable bytes field.

PathField — Filesystem path field (pathlib.Path).

File — Existing file path field.

Folder — Existing directory path field.

EnumField — Field for enum types.

LogLevel — Field for logging levels.

Choice — One-of choices validator field.

Details

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

Overview

```{eval-rst}
.. autosummary::
   :nosignatures:

   base.BaseStorage
   env.Env
   dot_env.DotEnv
   ini.Ini
   json.Json
   toml.Toml
   yaml_.Yaml
```

Base protocol and concrete backends

This page shows a brief index. Follow the links in the overview to get detailed documentation for each storage backend and the BaseStorage protocol.
