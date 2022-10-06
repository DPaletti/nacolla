from __future__ import annotations
from functools import singledispatchmethod
from typing import Callable, Generic, Tuple, Type, TypeVar, Union
import inspect

from nacolla.models import ImmutableModel
from nacolla.utilities import io_interface, register, union_types


_T = TypeVar("_T", bound=ImmutableModel)
_S = TypeVar("_S", bound=ImmutableModel)


class StatefulStep(Generic[_T, _S]):
    def __init__(self) -> None:
        self.input_interface: Type[_T]
        self.output_interface: Type[_S]
        self.single_dispatch_call: Callable[[_T], _S]
        public_methods = [
            method
            for method_name, method in inspect.getmembers(
                self, predicate=inspect.ismethod
            )
            if not method_name.startswith("_")
        ]

        if not public_methods:
            raise TypeError(
                "No public methods defined in "
                + str(self.__class__)
                + " please define the interface of your steps through public methods"
            )

        input_interfaces: Tuple[type, ...] = tuple()
        output_interfaces: Tuple[type, ...] = tuple()
        for public_method in public_methods:
            method_input_interface: type
            method_output_interface: type
            method_input_interface, method_output_interface = io_interface(
                public_method
            )
            input_interfaces += (method_input_interface,)
            output_interfaces += (method_output_interface,)

            register(self.__call__, public_method, union_types(method_input_interface))  # type: ignore

        self.input_interface = Union[input_interfaces]  # type: ignore
        self.output_interface = Union[output_interfaces]  # type: ignore

    @singledispatchmethod
    def __call__(self, input: ImmutableModel) -> ImmutableModel:
        raise NotImplementedError("Cannot handle input of type " + str(type(input)))
