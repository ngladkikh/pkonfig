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
    _mapper: Dict[Type, Type[TypedParameter]] = {
        int: IntParam,
        float: FloatParam,
        str: StrParam
    }
