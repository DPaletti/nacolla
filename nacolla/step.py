from __future__ import annotations
from typing import (
    Callable,
    Generic,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    Any,
)
from pydantic.fields import PrivateAttr

from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel

from nacolla.utilities import io_interface, union_types

_T_contra = TypeVar("_T_contra", bound=ImmutableModel, contravariant=True)
_S_contra = TypeVar("_S_contra", bound=ImmutableModel, contravariant=True)


class End:
    ...


class Step(GenericImmutableModel, Generic[_T_contra, _S_contra]):
    """A generic data transformation."""

    apply: Callable[[_T_contra], _S_contra]  # also class instances are callables
    next: Callable[[_S_contra], Union["Step[_S_contra, ImmutableModel]", End]]
    name: StrictStr
    _input_interface: Type[_T_contra] = PrivateAttr()
    _output_interface: Type[_S_contra] = PrivateAttr()

    def __init__(
        self,
        input_interface: Optional[Type[_T_contra]] = None,
        output_interface: Optional[Type[_S_contra]] = None,
        **data: Any,
    ):
        super().__init__(**data)
        apply_io: Tuple[Type[_T_contra], Type[_S_contra]] = io_interface(self.apply)

        self._input_interface: Type[_T_contra] = (
            apply_io[0] if not input_interface else input_interface
        )
        self._output_interface: Type[_S_contra] = (
            apply_io[1] if not output_interface else output_interface
        )

    def __call__(self, input: _T_contra):
        return self.apply(input)

    @property
    def input_interface(self):
        return union_types(self._input_interface)

    @property
    def output_interface(self):
        return union_types(self._output_interface)
