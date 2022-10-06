from functools import WRAPPER_UPDATES
from typing import Tuple, Union
from nacolla.step import End, Step
from tests.mock_models import (
    WrappedInt,
    WrappedDict,
    WrappedFloat,
    WrappedString,
)
from nacolla.stateful_step import StatefulStep


class Counter(StatefulStep[Union[WrappedInt, WrappedFloat], WrappedInt]):
    def __init__(self) -> None:
        super().__init__()
        self.counter: int = 0

    def add_int_to_counter(self, i: WrappedInt) -> WrappedInt:
        self.counter += i.a_int
        return WrappedInt(a_int=self.counter)

    def add_2float_to_counter(self, j: WrappedFloat) -> WrappedInt:
        self.counter += int(j.a_float * 2)
        return WrappedInt(a_int=self.counter)


class StringAdder(StatefulStep[WrappedString, WrappedString]):
    def __init__(self) -> None:
        super().__init__()
        self.s = ""

    def add_str(self, to_add: WrappedString) -> WrappedString:
        self.s = self.s + to_add.a_string
        return WrappedString(a_string=self.s)


def make_counter_step() -> Step[Union[WrappedInt, WrappedFloat], WrappedInt]:

    counter = Counter()

    return Step(
        apply=counter,
        next=End,
        name="counter",
        input_interface=counter.input_interface,
        output_interface=counter.output_interface,
    )


def make_string_adder_step() -> Step[WrappedString, WrappedString]:
    adder = StringAdder()

    return Step(
        apply=adder,
        next=End,
        name="adder",
        input_interface=adder.input_interface,
        output_interface=adder.output_interface,
    )


def make_steps() -> Tuple[
    Step[WrappedInt, WrappedString], Step[WrappedFloat, WrappedDict]
]:
    def _int_to_str(input: WrappedInt) -> WrappedString:
        return WrappedString(a_string=str(input.a_int))

    def _float_to_dict(input: WrappedFloat) -> WrappedDict:
        return WrappedDict(a_dict={"a_value": input.a_float})

    _s1: Step[WrappedInt, WrappedString] = Step(
        apply=_int_to_str, next=End, name="int_to_str"
    )

    _s2: Step[WrappedFloat, WrappedDict] = Step(
        apply=_float_to_dict, next=End, name="float_to_dict"
    )
    return _s1, _s2
