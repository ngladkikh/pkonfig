from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Optional, Type

from pkonfig.base import (
    BaseOuterConfig,
    BaseConfig,
    NOT_SET,
    TypeMapper,
    Field,
)
from pkonfig.fields import (
    Bool,
    Int,
    Float,
    Str,
    Byte,
    ByteArray,
    PathField,
    DecimalField,
)


class DefaultMapper(TypeMapper):
    type_mapping: Dict[Type, Type[Field]] = {
        bool: Bool,
        int: Int,
        float: Float,
        str: Str,
        bytes: Byte,
        bytearray: ByteArray,
        Path: PathField,
        Decimal: DecimalField,
    }

    def descriptor(self, type_: Type, value: Any = NOT_SET) -> Field:
        try:
            cls = self.type_mapping[type_]
            return cls(value)
        except KeyError:
            return value


class Config(BaseOuterConfig):
    _mapper = DefaultMapper()


class EmbeddedConfig(BaseConfig):
    _mapper = DefaultMapper()

    def __init__(self, alias: Optional[str] = None):
        self._alias = alias
