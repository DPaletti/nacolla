from typing import Any, Optional, Union
from pydantic import validator
from pydantic.types import StrictStr

from nacolla.models import ImmutableModel

KWARG_TYPE = Union[int, float, bool, str]
KWARGS_SPECIFICATION = Union[dict[str, KWARG_TYPE], dict[str, dict[str, KWARG_TYPE]]]


class Import(ImmutableModel):
    module: StrictStr
    name: Optional[StrictStr] = ""


class ImplementationSpecification(ImmutableModel):
    callable: Import
    name: StrictStr
    kwargs: Optional[KWARGS_SPECIFICATION] = {}

    @property
    def arguments(self) -> KWARGS_SPECIFICATION:
        if self.kwargs is None:
            raise Exception("Found none kwargs for step " + self.name)
        return self.kwargs

    @validator("kwargs")
    def _kwargs_for_empty_name(
        cls, kwargs_to_validate: Optional[KWARGS_SPECIFICATION], values: dict[str, Any]
    ):
        if kwargs_to_validate is not None:
            if values["name"] == "":
                for key, value in kwargs_to_validate.items():
                    if not type(value) is dict:
                        raise ValueError(
                            "In case no name is specified you must specify kwargs as a dict from function/class name to kwargs.\n"
                            + "Error found at key '"
                            + str(key)
                            + "' with value '"
                            + str(value)
                            + "' in "
                            + str(values["callable"])
                        )
        return kwargs_to_validate


class ImplementationMapSpecification(ImmutableModel):
    implementations: list[ImplementationSpecification]

    @validator("implementations")
    def validate_implementations(
        cls, implementations: list[ImplementationSpecification]
    ) -> list[ImplementationSpecification]:
        names: list[str] = [implementation.name for implementation in implementations]
        if len(names) > len(set(names)):
            raise ValueError(
                "Found duplicate names in the implementation map file, this is forbidden"
            )
        return implementations
