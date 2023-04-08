from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Generic,
    Mapping,
    Optional,
    Union,
    cast,
)
from typing_extensions import TypeGuard, Self
from pydantic import validator, StrictStr
from nacolla.models import StepModel, ImmutableModel


from nacolla.utilities.generics import INPUT_INTERFACE, INTERFACE, OUTPUT_INTERFACE
from nacolla.utilities.type_utilities import io_interface


class End:
    def __next__(self):
        raise StopIteration


class Step(StepModel, Generic[INPUT_INTERFACE, OUTPUT_INTERFACE]):
    """A generic data transformation."""

    name: StrictStr
    apply: Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]

    # Optional at initialization, if not passed they get assembled
    # Access not None versions through input and output properties
    input_interface: Optional[set[type[INPUT_INTERFACE]]] = None
    output_interface: Optional[set[type[OUTPUT_INTERFACE]]] = None

    # further type specification makes pydantic recurse indefinitely
    # this field gets assembled after their interfaces if not user provided
    next: Optional[dict[type[OUTPUT_INTERFACE], Any]] = None

    def concatenate(
        self,
        destination_step: Self,
        port: type[INTERFACE],
    ) -> None:
        """Concatenate with a destination step along a given port"""
        # TODO: check that concatenation is possible by removing the cast and
        # adding a typeguard
        # to check if the port is among the outputs of this step
        # and the inputs of the destination step

        if self.next is None:
            raise ValueError("None next found, cannot concatenate")
        if self._is_concatenation_compatible(port, destination_step):
            self.next[port] = destination_step
            return

        raise ValueError(
            "Concatenation between '"
            + str(self)
            + " ["
            + str(self.output)
            + "] "
            + "' and '"
            + str(destination_step)
            + " ["
            + str(destination_step.input)
            + "]"
            + "' along '"
            + str(port)
            + "' is incompatible"
        )

    def __eq__(self, other: object) -> bool:
        """Compute equality between two steps.
        Steps with the same name are always equal"""

        if not isinstance(other, Step):
            return False
        return self.name == other.name

    def __call__(self, input: INPUT_INTERFACE) -> OUTPUT_INTERFACE:
        """Apply this step to a given input"""

        return self.apply(input)

    def __next__(
        self,
    ) -> MappingProxyType[
        type[OUTPUT_INTERFACE],
        Union["Step[ImmutableModel, ImmutableModel]", End],
    ]:
        """Retrieve all the next steps and their corresponding types.
        A read-only non-none view of the next steps is returned"""

        if self.next is not None:
            return cast(
                MappingProxyType[
                    type[OUTPUT_INTERFACE],
                    Union[Self, End],
                ],
                MappingProxyType(self.next),
            )
        raise ValueError("Found none mapping in " + str(self))

    def __str__(
        self,
    ):
        """A step is fully represented by its name"""
        return self.name

    def next_step(
        self, port: type[ImmutableModel]
    ) -> "Union[Step[ImmutableModel, ImmutableModel], End]":
        next_mapping = next(self)

        if port in next_mapping.keys():
            return next_mapping[cast(type[OUTPUT_INTERFACE], port)]

        for available_out, step in next_mapping.items():
            if issubclass(port, available_out):
                return step

        raise ValueError(
            "Could not find "
            + str(type(port))
            + " among available output types: "
            + str(next_mapping)
        )

    def _is_concatenation_compatible(
        self, port: type, destination_step: Self
    ) -> TypeGuard[type[OUTPUT_INTERFACE]]:
        try:
            self.next_step(port)
            if port in destination_step.input:
                return True

            for destination_input in destination_step.input:
                if issubclass(destination_input, port):
                    return True

            return False
        except:
            return False

    @property
    def input(self) -> set[type[INPUT_INTERFACE]]:
        """Input interface"""

        return cast(set[type[INPUT_INTERFACE]], self.input_interface)

    @property
    def output(self) -> set[type[OUTPUT_INTERFACE]]:
        """Output interface"""

        return cast(set[type[OUTPUT_INTERFACE]], self.output_interface)

    @validator("input_interface", "output_interface", pre=True, always=True)
    def assemble_interface(
        cls, interface: Optional[set[type]], values: dict[str, Any]
    ) -> set[type]:
        """Assemble i/o interface from apply's type hints"""

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
    def validate_interface(cls, interface: set[type]) -> set[type[ImmutableModel]]:
        """Validate i/o interface with regard to type hints"""

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
        return cast(set[type[ImmutableModel]], interface)

    @validator("next")
    def validate_next(
        cls,
        to_validate: Mapping[
            type[ImmutableModel],
            Union[
                Self,
                End,
            ],
        ],
        values: dict[str, Any],
    ) -> Mapping[type[ImmutableModel], Union[Self, End,],]:
        """Validate mapping to next steps with respect to interface compatibility"""

        if not values.get("output_interface"):
            raise ValueError("Interface parsing failed")

        if to_validate is None:
            return {output: End() for output in values["output_interface"]}

        Step._no_dangling_output_type(
            set(to_validate.keys()), values["output_interface"]
        )
        Step._no_incompatible_mapping(mappings=to_validate)
        return to_validate

    @staticmethod
    def _no_dangling_output_type(
        mapped_output_types: set[type], transformation_output_interface: set[type]
    ) -> None:
        """Check if the mapping contains all the output types of the step's transformation"""

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
            type[OUTPUT_INTERFACE],
            Union[
                Self,  # type: ignore (pyright signals an obscure error)
                End,
            ],
        ]
    ) -> None:
        """Check compatibility between input and output type in a mapping"""

        for in_type, step in mappings.items():
            if not isinstance(step, End):
                step = cast(Step[ImmutableModel, ImmutableModel], step)
                if in_type not in step.input:
                    raise TypeError(
                        "Output type '"
                        + str(in_type)
                        + "' is forwarded to '"
                        + str(step)
                        + "' which does not accept such input.\n It accepts only '"
                        + str(step.input)
                        + "'."
                    )
