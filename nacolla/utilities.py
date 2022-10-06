from __future__ import annotations
import inspect
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, Set, Type, TypeVar, Tuple, get_args
from nacolla.models import ImmutableModel

if TYPE_CHECKING:  # pragma: no cover
    from nacolla.step import Step


_T = TypeVar("_T")
_S = TypeVar("_S")


def io_interface(function: Callable[[_T], _S]) -> Tuple[Type[_T], Type[_S]]:
    signature: inspect.Signature = inspect.signature(function)
    parameters: MappingProxyType[str, inspect.Parameter] = signature.parameters

    if len(parameters) > 1:
        raise TypeError(
            "Function '"
            + str(function)
            + "' has an invalid signature, too many parameters (exactly 1 required) '"
            + str(len(parameters))
            + "'"
        )

    input_interface: Type[_T] = list(parameters.values())[0].annotation

    if input_interface is inspect.Signature.empty:
        raise TypeError("Function '" + str(function) + "' is missing input annotation")

    output_interface: Type[_S] = signature.return_annotation

    if output_interface is inspect.Signature.empty:
        raise TypeError("Step '" + str(function) + "' is missing output annotation")

    return input_interface, output_interface


def union_types(union_type: type) -> Set[type]:
    u_types: Set[type] = set(get_args(union_type))
    if u_types:
        return u_types
    else:
        return {union_type}


_I = TypeVar("_I", bound=ImmutableModel)
_O = TypeVar("_O", bound=ImmutableModel)
_II = TypeVar("_II", bound=ImmutableModel)
_OO = TypeVar("_OO", bound=ImmutableModel)


def overlapping(s1: Step[_I, _O], s2: Step[_II, _OO]) -> bool:
    return bool(s1.input_interface.intersection(s2.input_interface))


def register(
    registar: Callable[[Any], Any],
    to_register: Callable[[Any], Any],
    to_register_interface: Set[type],
) -> None:
    for type_to_register in to_register_interface:
        registar.register(type_to_register)(to_register)  # type: ignore
