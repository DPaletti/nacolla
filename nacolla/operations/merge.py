from __future__ import annotations
from typing import Mapping, Type, TypeVar, Union
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

    if overlapping(s1, s2):
        raise TypeError(
            "Step '"
            + str(s1)
            + "' and '"
            + str(s2)
            + "' have overlapping input interfaces "
            + str(s1.input_interface)
            + " and "
            + str(s2.input_interface)
        )

    apply_dispatch = singledispatch(apply)
    register(apply_dispatch, s1, s1.input_interface)
    register(apply_dispatch, s2, s2.input_interface)

    merged_next: Mapping[
        Union[Type[_S], Type[_Q]],
        Union[Step[_S, ImmutableModel], Step[_Q, ImmutableModel], End],
    ] = {
        **next(s1),
        **next(s2),
    }

    return Step[Union[_T, _P], Union[_S, _Q]](
        apply=apply_dispatch,
        next=merged_next,
        name=str(s1) + "_" + str(s2),
        input_interface=s1.input_interface.union(s2.input_interface),
        output_interface=s1.output_interface.union(s2.output_interface),
    )
