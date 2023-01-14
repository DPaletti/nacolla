from typing import Dict, Union

from pydantic.types import StrictBool, StrictFloat, StrictInt, StrictStr
from pydantic import validator
from nacolla.models import ImmutableModel

STEP_INSTANTIATION_DESCRIPTION = Dict[
    str,
    Union[
        StrictStr,
        Dict[StrictStr, Union[StrictInt, StrictFloat, StrictBool, StrictStr]],
    ],
]


class StepInstantiation(ImmutableModel):
    description: Dict[str, STEP_INSTANTIATION_DESCRIPTION]

    @validator("description")
    def validate_description_structure(
        cls, description: STEP_INSTANTIATION_DESCRIPTION
    ):
        for key, value in description.items():
            if key == "init":
                if not type(value) is dict:
                    raise ValueError(
                        "Invalid 'init' found '"
                        + str(value)
                        + "' it must be a dictionary of keyword arguments to be passed to the step.\n"
                        + "Please do not use init as a type, it is a reserved name"
                    )
            else:
                if not type(value) is str:
                    raise ValueError(
                        "Invalid step found in mapping '"
                        + str(key)
                        + "' to '"
                        + str(value)
                        + "'. Each type must map to a step expressed as a string"
                    )


class FlowDescription(ImmutableModel):
    root: str
    steps: Dict[str, StepInstantiation]
