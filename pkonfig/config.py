from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Type

from pkonfig.base import NOT_SET, BaseConfig, Field, TypeMapper
from pkonfig.fields import (
    Bool,
    Byte,
    ByteArray,
    DecimalField,
    Float,
    Int,
    PathField,
    Str,
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

    def descriptor(self, type_, value: Any = NOT_SET) -> Field[Any]:
        try:
            cls = self.type_mapping[type_]
            return cls(value)
        except KeyError:
            return value


class Config(BaseConfig):
    _mapper = DefaultMapper()
