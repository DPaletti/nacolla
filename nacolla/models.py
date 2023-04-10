from __future__ import annotations
from pydantic import BaseModel
from pydantic.generics import GenericModel


class ImmutableModel(BaseModel):
    """Immutable Pydantic Model"""

    class Config:
        validate_all = True
        extra = "ignore"
        allow_mutation = False
        frozen = True
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        copy_on_model_validation = "deep"
        smart_union = True
        underscore_attrs_are_private = True


class StepModel(GenericModel):
    """Base model for steps"""

    class Config:
        validate_all = True
        extra = "ignore"
        use_enum_values = True
        validate_assignment = True
        arbitrary_types_allowed = True
        copy_on_model_validation = "deep"
        smart_union = True
        underscore_attrs_are_private = True
