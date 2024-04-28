from abc import ABC, ABCMeta, abstractmethod
from collections import ChainMap
from collections.abc import Mapping
from inspect import getmro, isclass, isdatadescriptor
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Optional,
    Reversible,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

# from pkonfig.fields import Field, NOT_SET
from pkonfig.storage.base import BaseStorage, DictStorage, InternalKey

TypeMapping = Dict[Type, Type["Field"]]
C = TypeVar("C", bound="BaseConfig")
T = TypeVar("T")


class TypeMapper(ABC):
    """Replaces user defined attributes with typed descriptors"""

    type_mapping: TypeMapping = {}

    def __init__(self, mappings: Optional[TypeMapping] = None):
        if mappings:
            self.type_mapping.update(mappings)

    def replace_fields_with_descriptors(
        self, attributes: Dict[str, Any], type_hints: Dict[str, Type]
    ) -> None:
        inner_configs = []
        attribute_names = []
        # for name in filter(self.public_attribute, type_hints.keys()):
        #     attribute = attributes.get(name, NOT_SET)
        #     if self.replace(attribute):
        #         hint = type_hints[name]
        #         descriptor = self.descriptor(hint, attribute)
        #         attributes[name] = descriptor
        #         if isinstance(attribute, BaseConfig):
        #             inner_configs.append(attribute)
        #         else:
        #             attribute_names.append(name)
        # attributes["_inner_configs"] = inner_configs
        # attributes["_field_names"] = attribute_names

    @staticmethod
    def public_attribute(attr_name: str) -> bool:
        return not attr_name.startswith("_")

    @staticmethod
    def replace(attribute: Any):
        return not (isdatadescriptor(attribute) or isclass(attribute))

    # @abstractmethod
    # def descriptor(self, type_: T, value: Any = NOT_SET) -> Field[T]:
    #     pass


class MetaConfig(ABCMeta):
    """Replaces class-level attributes with Field descriptors"""

    def __new__(mcs, name, parents, attributes):  # pylint: disable=arguments-differ
        MetaConfig.extend_annotations(attributes)
        mapper = MetaConfig.get_mapper(attributes, parents)
        if mapper:
            mapper.replace_fields_with_descriptors(
                attributes, attributes.get("__annotations__", {})
            )
        config_class = super().__new__(mcs, name, parents, attributes)
        for attr_name in filter(MetaConfig.public_attribute, attributes):
            attr = attributes[attr_name]
            if MetaConfig.is_config_class(attr):
                print("Inner config: {} {}".format(name, attr))
                attr.get_storage = getattr(config_class, "get_storage")

        return config_class

    @staticmethod
    def is_config_class(attribute: Any) -> bool:
        for base_class in getmro(type(attribute)):
            if base_class.__class__ is MetaConfig:
                return True
        return False

    @staticmethod
    def public_attribute(attr_name: str) -> bool:
        return not attr_name.startswith("_")

    @classmethod
    def extend_annotations(cls, attributes: Dict[str, Any]) -> None:
        """Extends class annotations using default values types or fields cast method annotation"""
        annotations = attributes.get("__annotations__", {})
        # for name in filter(cls.public_attribute, attributes.keys()):
        #     if name not in annotations:
        #         attr_type = type(attr)
        #         if issubclass(attr_type, Field):
        #             annotation = get_type_hints(attr.cast).get("return", Any)
        #         else:
        #             annotation = attr_type
        #         annotations[name] = annotation
        # attributes["__annotations__"] = annotations

    @staticmethod
    def get_mapper(
        attributes: Dict[str, Any], parents: Reversible[Type]
    ) -> Optional[TypeMapper]:
        """Get mapper from class attribute or take it from parent"""

        mapper = attributes.get("_mapper")
        if mapper and isinstance(mapper, TypeMapper):
            return mapper

        for cls in reversed(parents):
            mapper = getattr(cls, "_mapper", None)
            if mapper and isinstance(mapper, TypeMapper):
                return mapper
        return None
