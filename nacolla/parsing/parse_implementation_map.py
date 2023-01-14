from __future__ import annotations
from functools import reduce
from pathlib import Path
from typing import Any, Callable, Dict, List, Type, Union, cast
import json
from typing_extensions import TypeGuard
from nacolla.models import ImmutableModel
from nacolla.operations import merge
from nacolla.parsing.implementation_map_file_specification import (
    KWARG_TYPE,
    KWARGS_SPECIFICATION,
    ImplementationMapSpecification,
)
from nacolla.parsing.parse_implementation import (
    ABSTRACT_STEP,
    IMPLEMENTATION,
    parse_implementation,
)
from nacolla.stateful_callable import StatefulCallable, make_stateful_step
from nacolla.step import Step
import inspect

IMPLEMENTATION_MAP = Dict[str, Step[ImmutableModel, ImmutableModel]]


def parse_implementation_map(
    implementation_map_file: Path,
) -> IMPLEMENTATION_MAP:
    specification: ImplementationMapSpecification = ImplementationMapSpecification(
        **json.loads(implementation_map_file.read_text())
    )

    implementation_dict: IMPLEMENTATION_MAP = {}
    for step in specification.implementations:

        parsed_implementation: IMPLEMENTATION = parse_implementation(
            import_definition=step.callable
        )
        if _to_merge(parsed_implementation):
            implementation_dict[step.name] = _parse_steps_and_merge(
                parsed_implementation, step.arguments, step.name
            )

        else:
            implementation_dict[step.name] = _parse_step(
                step.name,
                cast(
                    ABSTRACT_STEP,
                    parsed_implementation,
                ),
                kwargs=step.arguments,
            )

    return implementation_dict


def _parse_steps_and_merge(
    callable_dict: Dict[
        str,
        ABSTRACT_STEP,
    ],
    kwargs: KWARGS_SPECIFICATION,
    step_name: str,
):

    step_accumulator: List[Step[ImmutableModel, ImmutableModel]] = []
    for callable_name, callable_func in callable_dict.items():
        step_accumulator.append(
            _parse_step(callable_name, callable_func, kwargs=kwargs)
        )
    merged_step = reduce(merge, step_accumulator)  # type: ignore
    merged_step.name = step_name
    return merged_step


def _parse_step(
    callable_name: str,
    callable_func: ABSTRACT_STEP,
    kwargs: KWARGS_SPECIFICATION,
):
    parsed_kwargs: Dict[str, KWARG_TYPE] = cast(
        Dict[str, KWARG_TYPE],
        kwargs.get(callable_name)
        if isinstance(kwargs.get(callable_name), dict)
        else kwargs,
    )
    if _is_stateful_callable(callable_func):
        return make_stateful_step(callable_func(**parsed_kwargs), name=callable_name)

    if _is_callable(callable_func):
        return Step[ImmutableModel, ImmutableModel](
            name=callable_name, apply=callable_func
        )

    raise ValueError(
        "Could not build step from '"
        + str(callable_func)
        + "' got from '"
        + str(callable_name)
    )


def _is_stateful_callable(
    to_check: Any,
) -> TypeGuard[Type[StatefulCallable[ImmutableModel, ImmutableModel]]]:
    return inspect.isclass(to_check) and issubclass(to_check, StatefulCallable)


def _is_callable(
    to_check: Any,
) -> TypeGuard[Callable[[ImmutableModel], ImmutableModel]]:
    return callable(to_check)


def _to_merge(
    implementation: IMPLEMENTATION,
) -> TypeGuard[
    Dict[
        str,
        Union[
            Callable[[ImmutableModel], ImmutableModel],
            Type[StatefulCallable[Any, Any]],
        ],
    ],
]:
    return isinstance(implementation, dict)
