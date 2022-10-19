from __future__ import annotations
from typing import Mapping, Set, Type, TypeVar, Union, cast
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
            + str(s1.input)
            + " and "
            + str(s2.input)
        )

    apply_dispatch = singledispatch(apply)
    register(apply_dispatch, s1, cast(Set[type], s1.input))
    register(apply_dispatch, s2, cast(Set[type], s2.input))

    merged_next: Mapping[
        Union[Type[_S], Type[_Q]],
        Union[Step[_S, ImmutableModel], Step[_Q, ImmutableModel], End],
    ] = {
        **next(s1),
        **next(s2),
    }

    return Step[Union[_T, _P], Union[_S, _Q]](
        input_interface=s1.input.union(s2.input),
        output_interface=s1.output.union(s2.output),
        apply=apply_dispatch,
        name=str(s1) + "_" + str(s2),
        next=merged_next,
    )
