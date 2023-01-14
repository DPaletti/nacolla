from __future__ import annotations
from typing import Callable, Generic
import inspect
from nacolla.step import End, Step

from nacolla.utilities import io_interface
from nacolla.utilities.generics import INPUT_INTERFACE, OUTPUT_INTERFACE
from abc import ABC


class StatefulCallable(ABC, Generic[INPUT_INTERFACE, OUTPUT_INTERFACE]):
    def __init__(self) -> None:
        """Parse the i/o interface of the children from its public classes"""

        self.input_interface: set[type[INPUT_INTERFACE]] = set()
        self.output_interface: set[type[OUTPUT_INTERFACE]] = set()
        self.dispatch_dict: dict[
            type, Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]
        ] = {}

        public_methods: list[
            Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]
        ] = self._get_all_public_methods()

        for public_method in public_methods:
            input_interface, output_interface = StatefulCallable._parse_interface(
                public_method
            )
            self.input_interface |= input_interface
            self.output_interface |= output_interface

            self._update_dispatch_dict(input_interface, public_method)

    def __call__(self, input: INPUT_INTERFACE) -> OUTPUT_INTERFACE:
        """Route the input to the correct handler given its type and apply the transformation"""

        handler = self.dispatch_dict.get(type(input))
        if not handler:
            raise NotImplementedError("Cannot handle input of type " + str(type(input)))
        return handler(input)

    def _get_all_public_methods(
        self,
    ) -> list[Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]]:
        """Retrieve all the public methods of the children"""

        public_methods = [
            method
            for method_name, method in inspect.getmembers(
                self, predicate=inspect.ismethod
            )
            if not method_name.startswith("_") or method_name == "call"
        ]

        if not public_methods:
            raise TypeError(
                "No public methods defined in "
                + str(self.__class__)
                + " please define the interface of your steps through public methods"
            )
        return public_methods

    @staticmethod
    def _parse_interface(
        public_method: Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE]
    ) -> tuple[set[type[INPUT_INTERFACE]], set[type[OUTPUT_INTERFACE]]]:
        """Parse the IO interface of a public method"""

        method_input_interface, method_output_interface = (
            Step.validate_interface(interface)
            for interface in io_interface(public_method)
        )
        return method_input_interface, method_output_interface

    def _update_dispatch_dict(
        self,
        input_interface: set[type[INPUT_INTERFACE]],
        public_method: Callable[[INPUT_INTERFACE], OUTPUT_INTERFACE],
    ):
        """Update the dispatching dictionary with a new input interface and method"""

        for interface_type in input_interface:
            self.dispatch_dict[interface_type] = public_method


def make_stateful_step(
    stateful_callable: StatefulCallable[INPUT_INTERFACE, OUTPUT_INTERFACE], name: str
) -> Step[INPUT_INTERFACE, OUTPUT_INTERFACE]:
    return Step[INPUT_INTERFACE, OUTPUT_INTERFACE](
        apply=stateful_callable,
        name=name,
        next={output: End() for output in stateful_callable.output_interface},
        input_interface=stateful_callable.input_interface,
        output_interface=stateful_callable.output_interface,
    )
