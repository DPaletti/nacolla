from __future__ import annotations
from types import MappingProxyType
from typing import (
    Callable,
    Generic,
    Mapping,
    Optional,
    Set,
    Tuple,
    TypeVar,
    Union,
    Any,
    Type,
)
from pydantic.fields import PrivateAttr
from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel


from nacolla.utilities import io_interface


_INPUT_INTERFACE = TypeVar(
    "_INPUT_INTERFACE",
    bound=ImmutableModel,
    contravariant=True,
)
_OUTPUT_INTERFACE = TypeVar(
    "_OUTPUT_INTERFACE",
    bound=ImmutableModel,
    covariant=True,
)


class End:
    def __next__(self):
        raise StopIteration


class Step(GenericImmutableModel, Generic[_INPUT_INTERFACE, _OUTPUT_INTERFACE]):
    """A generic data transformation."""

    _name: StrictStr = PrivateAttr()
    _next: Mapping[
        Type[_OUTPUT_INTERFACE],
        Union[
            "Step[_OUTPUT_INTERFACE, ImmutableModel]",
            End,
        ],
    ] = PrivateAttr()
    _apply: Callable[[_INPUT_INTERFACE], _OUTPUT_INTERFACE] = PrivateAttr()
    _input_interface: Set[type] = PrivateAttr()
    _output_interface: Set[type] = PrivateAttr()

    def __init__(
        self,
        name: StrictStr,
        next: Mapping[
            Type[_OUTPUT_INTERFACE],
            Union[
                "Step[_OUTPUT_INTERFACE, ImmutableModel]",
                End,
            ],
        ],
        apply: Callable[[_INPUT_INTERFACE], _OUTPUT_INTERFACE],
        input_interface: Optional[Set[type]] = None,
        output_interface: Optional[Set[type]] = None,
        **data: Any,
    ):
        super().__init__(**data)
        self._name = name
        self._next = next
        self._apply = apply
        apply_io_interface: Tuple[Set[type], Set[type]] = io_interface(self._apply)

        self._input_interface = (
            apply_io_interface[0] if not input_interface else input_interface
        )
        self._output_interface = (
            apply_io_interface[1] if not output_interface else output_interface
        )

    def __call__(self, input: _INPUT_INTERFACE) -> _OUTPUT_INTERFACE:
        return self._apply(input)

    def __next__(
        self,
    ) -> MappingProxyType[
        Type[_OUTPUT_INTERFACE],
        Union["Step[_OUTPUT_INTERFACE, ImmutableModel]", End],
    ]:
        return MappingProxyType(self._next)

    @property
    def input_interface(self) -> Set[type]:
        """The set of accepted types."""
        return self._input_interface

    @property
    def output_interface(self) -> Set[type]:
        """The set of returned types."""
        return self._output_interface
