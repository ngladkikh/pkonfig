from typing import Any, Dict, Type, Union

from pkonfig.base import BaseOuterConfig, BaseInnerConfig, NOT_SET, TypeMapper, TypedParameter
from pkonfig.fields import IntParam, FloatParam, StrParam


ConfigT = Union["Config", "EmbeddedConfig"]


class DefaultMapper(TypeMapper):
    _mapper: Dict[Type, Type[TypedParameter]] = {
        int: IntParam,
        float: FloatParam,
        str: StrParam
    }

    def descriptor(
        self, type_: Type, value: Any = NOT_SET
    ) -> TypedParameter:
        cls = self._mapper.get(type_, StrParam)
        return cls(value)


class Config(BaseOuterConfig):
    Mapper = DefaultMapper


class EmbeddedConfig(BaseInnerConfig):
    Mapper = DefaultMapper
