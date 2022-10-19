from typing import Type, TypeVar
from nacolla.models import ImmutableModel
from nacolla.step import Step


_T = TypeVar("_T", bound=ImmutableModel)
_S = TypeVar("_S", bound=ImmutableModel)


def concatenate(
    s1: Step[_T, _S], s2: Step[_S, ImmutableModel], port: Type[_S]
) -> Step[_T, _S]:
    concatenated_next = dict(next(s1))

    if not concatenated_next.get(port):
        raise TypeError(
            "Step " + str(s1) + " does not support output type " + str(port)
        )

    concatenated_next[port] = s2
    return Step(
        name=str(s1),
        next=concatenated_next,
        apply=s1.__call__,
        input_interface=s1.input,
        output_interface=s1.output,
    )
