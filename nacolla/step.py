from __future__ import annotations
from types import MappingProxyType
from typing import Callable, Generic, Type, TypeVar, Union, Any
from pydantic.fields import PrivateAttr

from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel
import inspect

_T_co = TypeVar("_T_co", bound=ImmutableModel, contravariant=True)
_S_co = TypeVar("_S_co", bound=ImmutableModel, contravariant=True)


class Step(GenericImmutableModel, Generic[_T_co, _S_co]):
    """A generic data transformation."""

    apply: Callable[[_T_co], _S_co]
    next: Callable[[_S_co], Union["Step[_S_co, ImmutableModel]", _S_co]]
    name: StrictStr
    _input_interface: Type[_T_co] = PrivateAttr()
    _output_interface: Type[_S_co] = PrivateAttr()

    def __init__(self, **data: Any):
        super().__init__(**data)
        apply_signature: inspect.Signature = inspect.signature(self.apply)
        parameters: MappingProxyType[
            str, inspect.Parameter
        ] = apply_signature.parameters
        if len(parameters) > 1:
            raise TypeError(
                "Step '"
                + self.name
                + "' has an invalid signature, too many parameters (exactly 1 required) '"
                + str(len(parameters))
                + "'"
            )

        self._input_interface: Type[_T_co] = list(parameters.values())[0].annotation
        if self._input_interface is inspect.Signature.empty:
            raise TypeError("Step '" + self.name + "' is missing input annotation")

        self._output_interface: Type[_S_co] = apply_signature.return_annotation
        if self._output_interface is inspect.Signature.empty:
            raise TypeError("Step '" + self.name + "' is missing output annotation")

    @property
    def input_interface(self):
        return self._input_interface

    @property
    def output_interface(self):
        return self._output_interface
