from typing import Any, Dict, Type

from pkonfig.base import (
    BaseOuterConfig,
    BaseInnerConfig,
    NOT_SET,
    TypeMapper,
    TypedParameter,
)
from pkonfig.fields import (
    Int,
    Float,
    Str,
    Byte,
    AnyType,
    ByteArray,
)


class DefaultMapper(TypeMapper):
    _mapper: Dict[Type, Type[TypedParameter]] = {
        int: Int,
        float: Float,
        str: Str,
        bytes: Byte,
        bytearray: ByteArray,
    }

    def descriptor(self, type_: Type, value: Any = NOT_SET) -> TypedParameter:
        cls = self._mapper.get(type_, AnyType)
        return cls(value)


class Config(BaseOuterConfig):
    Mapper = DefaultMapper


class EmbeddedConfig(BaseInnerConfig):
    Mapper = DefaultMapper
