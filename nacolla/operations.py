from typing import Type, TypeVar, Union, get_args

from nacolla.models import ImmutableModel
from nacolla.step import Step
from functools import singledispatch


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
    ) -> Union[Step[Union[_S, _Q], ImmutableModel], Union[_S, _Q]]:
        raise NotImplementedError

    if s1.input_interface is s2.input_interface or set(
        get_args(s1.input_interface)
    ).intersection(set(get_args(s2.input_interface))):
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
    apply_dispatch.register(s1.apply)
    apply_dispatch.register(s2.apply)

    next_dispatch = singledispatch(next)
    next_dispatch.register(s1.next)
    next_dispatch.register(s2.next)

    return Step[Union[_T, _P], Union[_S, _Q]](
        apply=apply_dispatch,
        next=next_dispatch,
        name=s1.name + "_" + s2.name,
        input_interface=Union[s1.input_interface, s2.input_interface],  # type: ignore
        output_interface=Union[s1.output_interface, s2.output_interface],  # type: ignore
    )
