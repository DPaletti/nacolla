from __future__ import annotations
from typing import TypeVar, Union

from nacolla.models import ImmutableModel
from nacolla.step import End, Step
from functools import singledispatch

from nacolla.utilities import overlapping, register


_T = TypeVar("_T", bound=ImmutableModel)
_S = TypeVar("_S", bound=ImmutableModel)
_P = TypeVar("_P", bound=ImmutableModel)
_Q = TypeVar("_Q", bound=ImmutableModel)


def merge(s1: Step[_T, _S], s2: Step[_P, _Q]) -> Step[Union[_T, _P], Union[_S, _Q]]:
    """Merge two steps in one.
    The step resulting from the merge handles the union of the types that the two handle.
    Steps with overlapping interfaces cannot be merged.
    """

    def apply(input: Union[_T, _P]) -> Union[_S, _Q]:
        raise NotImplementedError

    def next(
        to_dispatch: Union[_S, _Q]
    ) -> Union[Step[Union[_S, _Q], ImmutableModel], End]:
        raise NotImplementedError

    if overlapping(s1, s2):
        raise TypeError(
            "Step '"
            + s1.name
            + "' and '"
            + s2.name
            + "' have overlapping input interfaces "
            + str(s1.input_interface)
            + " and "
            + str(s2.input_interface)
        )

    apply_dispatch = singledispatch(apply)
    register(apply_dispatch, s1.apply, s1.input_interface)
    register(apply_dispatch, s2.apply, s2.input_interface)

    next_dispatch = singledispatch(next)
    register(next_dispatch, s1.next, s1.output_interface)
    register(next_dispatch, s2.next, s2.output_interface)

    return Step[Union[_T, _P], Union[_S, _Q]](
        apply=apply_dispatch,
        next=next_dispatch,
        name=s1.name + "_" + s2.name,
        input_interface=Union[s1.raw_input_interface, s2.raw_input_interface],  # type: ignore
        output_interface=Union[s1.raw_output_interface, s2.raw_output_interface],  # type: ignore
    )
