from __future__ import annotations
from types import MappingProxyType
from typing import Callable, Generic, Optional, Type, TypeVar, Union, Any
from pydantic.fields import PrivateAttr

from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel
import inspect

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

        self._input_interface: Type[_T_contra] = (
            list(parameters.values())[0].annotation
            if not input_interface
            else input_interface
        )
        if self._input_interface is inspect.Signature.empty:
            raise TypeError("Step '" + self.name + "' is missing input annotation")

        self._output_interface: Type[_S_contra] = (
            apply_signature.return_annotation
            if not output_interface
            else output_interface
        )
        if self._output_interface is inspect.Signature.empty:
            raise TypeError("Step '" + self.name + "' is missing output annotation")

    @property
    def input_interface(self):
        return self._input_interface

    @property
    def output_interface(self):
        return self._output_interface
