from __future__ import annotations
from functools import singledispatchmethod
from typing import Generic, Set, TypeVar
import inspect

from nacolla.models import ImmutableModel
from nacolla.utilities import io_interface, register


_INPUT_INTERFACE = TypeVar("_INPUT_INTERFACE", bound=ImmutableModel, contravariant=True)
_OUTPUT_INTERFACE = TypeVar("_OUTPUT_INTERFACE", bound=ImmutableModel, covariant=True)


class StatefulStep(Generic[_INPUT_INTERFACE, _OUTPUT_INTERFACE]):
    def __init__(self) -> None:
        self.input_interface: Set[type]
        self.output_interface: Set[type]
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

        input_interfaces: Set[type] = set()
        output_interfaces: Set[type] = set()
        for public_method in public_methods:
            method_input_interface: Set[type]
            method_output_interface: Set[type]
            method_input_interface, method_output_interface = io_interface(
                public_method
            )
            input_interfaces |= method_input_interface
            output_interfaces |= method_output_interface

            register(self.__call__, public_method, method_input_interface)

        self.input_interface = input_interfaces
        self.output_interface = output_interfaces

    @singledispatchmethod
    def __call__(self, input: _INPUT_INTERFACE) -> _OUTPUT_INTERFACE:
        raise NotImplementedError("Cannot handle input of type " + str(type(input)))
