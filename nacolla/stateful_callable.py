from __future__ import annotations
from functools import singledispatchmethod
from typing import Generic, Set, Type, cast
import inspect
from nacolla.step import End, Step

from nacolla.utilities import io_interface, register
from nacolla.utilities.generics import INPUT_INTERFACE, OUTPUT_INTERFACE


class StatefulCallable(Generic[INPUT_INTERFACE, OUTPUT_INTERFACE]):
    def __init__(self) -> None:
        self.input_interface: Set[Type[INPUT_INTERFACE]]
        self.output_interface: Set[Type[OUTPUT_INTERFACE]]

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

        input_interfaces: Set[Type[INPUT_INTERFACE]] = set()
        output_interfaces: Set[Type[OUTPUT_INTERFACE]] = set()
        for public_method in public_methods:
            method_input_interface: Set[Type[INPUT_INTERFACE]]
            method_output_interface: Set[Type[OUTPUT_INTERFACE]]
            method_input_interface, method_output_interface = (
                Step.validate_interface(interface)
                for interface in io_interface(public_method)
            )
            input_interfaces |= method_input_interface
            output_interfaces |= method_output_interface

            register(
                self.__call__, public_method, cast(Set[type], method_input_interface)
            )

        self.input_interface = input_interfaces
        self.output_interface = output_interfaces

    @singledispatchmethod
    def __call__(self, input: INPUT_INTERFACE) -> OUTPUT_INTERFACE:
        raise NotImplementedError("Cannot handle input of type " + str(type(input)))


def step(
    stateful_callable: StatefulCallable[INPUT_INTERFACE, OUTPUT_INTERFACE], name: str
) -> Step[INPUT_INTERFACE, OUTPUT_INTERFACE]:
    return Step[INPUT_INTERFACE, OUTPUT_INTERFACE](
        apply=stateful_callable.__call__,
        name=name,
        next={output: End() for output in stateful_callable.output_interface},
        input_interface=stateful_callable.input_interface,
        output_interface=stateful_callable.output_interface,
    )
