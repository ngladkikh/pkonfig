from typing import Any, Dict, Type

from pkonfig.base import (
    BaseOuterConfig,
    BaseInnerConfig,
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
)


class DefaultMapper(TypeMapper):
    _mapper: Dict[Type, Type[Field]] = {
        bool: Bool,
        int: Int,
        float: Float,
        str: Str,
        bytes: Byte,
        bytearray: ByteArray,
    }

    def descriptor(self, type_: Type, value: Any = NOT_SET) -> Field:
        try:
            cls = self._mapper[type_]
            return cls(value)
        except KeyError:
            return value


class Config(BaseOuterConfig):
    Mapper = DefaultMapper()


class EmbeddedConfig(BaseInnerConfig):
    Mapper = DefaultMapper()
