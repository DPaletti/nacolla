from __future__ import annotations
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Mapping,
    Optional,
    Set,
    Union,
    Type,
    cast,
)
from pydantic.class_validators import validator
from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel


from nacolla.utilities.generics import INPUT_INTERFACE, OUTPUT_INTERFACE
from nacolla.utilities.type_utilities import io_interface


class End:
    def __next__(self):
        raise StopIteration


class Step(GenericImmutableModel, Generic[INPUT_INTERFACE, OUTPUT_INTERFACE]):
    """A generic data transformation."""

    name: StrictStr
    apply: Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]

    # Optional at initialization but required for the model
    # If not passed they are assembled
    # Access not None versions through input and output properties
    input_interface: Optional[Set[Type[INPUT_INTERFACE]]] = None
    output_interface: Optional[Set[Type[OUTPUT_INTERFACE]]] = None

    next: Mapping[
        Type[OUTPUT_INTERFACE],
        Union[
            "Step[OUTPUT_INTERFACE, ImmutableModel]",
            End,
        ],
    ]

    def __call__(self, input: INPUT_INTERFACE) -> OUTPUT_INTERFACE:
        return self.apply(input)

    def __next__(
        self,
    ) -> MappingProxyType[
        Type[OUTPUT_INTERFACE],
        Union["Step[OUTPUT_INTERFACE, ImmutableModel]", End],
    ]:
        return MappingProxyType(self.next)

    def __str__(
        self,
    ):
        return self.name

    @property
    def input(self) -> Set[Type[INPUT_INTERFACE]]:
        return cast(Set[Type[INPUT_INTERFACE]], self.input_interface)

    @property
    def output(self) -> Set[Type[OUTPUT_INTERFACE]]:
        return cast(Set[Type[OUTPUT_INTERFACE]], self.output_interface)

    @validator("input_interface", "output_interface", pre=True, always=True)
    def assemble_interface(
        cls, interface: Optional[Set[type]], values: Dict[str, Any]
    ) -> Set[type]:
        if interface is not None:
            # interface set by user
            return interface

        apply = values["apply"]

        input_interface, output_interface = io_interface(apply)
        if not values.get("input_interface"):
            return input_interface
        if not values.get("output_interface"):
            return output_interface

        raise ValueError(
            "Input Interface and Output interface are already set, with values "
            + str(values.get("input_interface"))
            + " and "
            + str(values.get("output_interface"))
        )

    @validator("input_interface", "output_interface")
    def validate_interface(cls, interface: Set[type]) -> Set[Type[ImmutableModel]]:

        if any(
            [
                not issubclass(interface_type, ImmutableModel)
                for interface_type in interface
            ]
        ):
            raise TypeError(
                "Input interface '"
                + "' must be either a subclass of ImmutableModel or a union of subclasses of ImmutableModel found "
                + str(interface)
            )
        return cast(Set[Type[ImmutableModel]], interface)

    @validator("next")
    def validate_next(
        cls,
        to_validate: Mapping[
            Type[ImmutableModel],
            Union[
                "Step[OUTPUT_INTERFACE, ImmutableModel]",
                End,
            ],
        ],
        values: Dict[str, Any],
    ) -> Mapping[
        Type[ImmutableModel],
        Union[
            "Step[OUTPUT_INTERFACE, ImmutableModel]",
            End,
        ],
    ]:
        if not values.get("output_interface"):
            raise ValueError("Interface parsing failed")
        Step._no_dangling_output_type(
            set(to_validate.keys()), values["output_interface"]
        )
        Step._no_incompatible_mapping(mappings=to_validate)
        return to_validate

    @staticmethod
    def _no_dangling_output_type(
        mapped_output_types: Set[type], transformation_output_interface: Set[type]
    ) -> None:
        if not mapped_output_types == transformation_output_interface:
            raise TypeError(
                "Output types of step transformations are '"
                + str(mapped_output_types)
                + "'.\n While output types represented in the mapping to next steps are '"
                + str(transformation_output_interface)
                + "'. These two must be equal"
            )

    @staticmethod
    def _no_incompatible_mapping(
        mappings: Mapping[
            Type[OUTPUT_INTERFACE],
            Union[
                "Step[OUTPUT_INTERFACE, ImmutableModel]",
                End,
            ],
        ]
    ) -> None:
        for in_type, step in mappings.items():
            if type(step) is not End:
                step = cast(Step[ImmutableModel, ImmutableModel], step)
                if in_type not in step.output:
                    raise TypeError(
                        "Output type '"
                        + str(in_type)
                        + "' is forwarded to '"
                        + str(step)
                        + "' which does not accept such input.\n It accepts only '"
                        + str(step.input_interface)
                        + "'."
                    )
