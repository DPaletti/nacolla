from __future__ import annotations
from typing import (
    Any,
    Union,
    Callable,
    get_args,
    get_origin,
    get_type_hints,
)


def unwrap_union(to_unwrap: type) -> set[type]:
    """Unwrap a union type in the set of composing types"""

    if get_origin(to_unwrap) is Union:
        return set(get_args(to_unwrap))
    else:
        return {to_unwrap}


def io_interface(function: Callable[[Any], Any]) -> tuple[set[type], set[type]]:
    """retrieve the io_interface of a function from its type hints"""

    type_hints: dict[str, type] = get_type_hints(function)

    if not type_hints.get("return"):
        raise TypeError("Step '" + str(function) + "' is missing output annotation")
    if len(type_hints) == 1:
        raise TypeError("Function '" + str(function) + "' is missing input annotation")
    if len(type_hints) > 2:
        raise TypeError(
            "Function '"
            + str(function)
            + "' has an invalid signature, too many parameters (exactly 1 required) '"
            + str(len(type_hints) - 1 - 1)
            + "'"
        )

    input_interface: set[type] = unwrap_union(list(type_hints.values())[0])

    output_interface: set[type] = unwrap_union(list((type_hints).values())[1])

    return input_interface, output_interface
