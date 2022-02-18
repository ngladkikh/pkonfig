from pathlib import Path
from typing import Any, Dict, Mapping, Type, TypeVar, Union

from pkonfig.base import AbstractBaseConfig, TypedParameter
from pkonfig.fields import IntParam, FloatParam, StrParam


Values = Union[str, int, float, Path]
ConfigStorage = Mapping[str, Any]
Config = Union["OuterMostConfig", "EmbeddedConfig"]
TEmbedded = TypeVar("TEmbedded", bound="EmbeddedConfig")
Annotations = Dict[str, Type]


class BaseConfig(AbstractBaseConfig):
    _type_map: Dict[Type, TypedParameter] = {
        int: IntParam,
        float: FloatParam,
        str: StrParam
    }

    @classmethod
    def get_descriptor(cls, annotation: Type, value: Any) -> TypedParameter:
        descriptor_class = cls._type_map.get(annotation, StrParam)
        return descriptor_class(value)
