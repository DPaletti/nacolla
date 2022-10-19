from __future__ import annotations
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Set,
    TypeVar,
)

from nacolla.models import ImmutableModel

if TYPE_CHECKING:
    from nacolla.step import Step  # pragma: no cover


_I = TypeVar("_I", bound=ImmutableModel)
_O = TypeVar("_O", bound=ImmutableModel)
_II = TypeVar("_II", bound=ImmutableModel)
_OO = TypeVar("_OO", bound=ImmutableModel)


def overlapping(s1: Step[_I, _O], s2: Step[_II, _OO]) -> bool:
    return bool(s1.input.intersection(s2.input))


def register(
    registar: Callable[[Any], Any],
    to_register: Callable[[Any], Any],
    to_register_interface: Set[type],
) -> None:
    for type_to_register in to_register_interface:
        print(
            "Registering: "
            + str(to_register)
            + " to type "
            + str(type_to_register)
            + " on "
            + str(registar)
        )
        registar.register(type_to_register)(to_register)  # type: ignore
