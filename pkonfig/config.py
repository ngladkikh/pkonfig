from decimal import Decimal
from pathlib import Path
from typing import Any, Dict, Type

from pkonfig.base import (
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


class Config(BaseConfig):
    _mapper = DefaultMapper()
