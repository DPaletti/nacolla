import importlib.machinery
import inspect
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Union, cast, Optional
from typing_extensions import TypeAlias, TypeGuard

from nacolla.models import ImmutableModel
from nacolla.parsing.implementation_map_file_specification import Import
from nacolla.stateful_callable import StatefulCallable

ABSTRACT_STEP = Union[
    Callable[[ImmutableModel], ImmutableModel], type[StatefulCallable[Any, Any]]
]

IMPLEMENTATION: TypeAlias = Union[
    ABSTRACT_STEP,
    dict[str, ABSTRACT_STEP],
]


def parse_implementation(import_definition: Import) -> IMPLEMENTATION:
    module: ModuleType = _load_module(import_definition)

    if _is_specific_import(import_definition.name):
        abstract_step: ABSTRACT_STEP = _retrieve_function(
            module, import_definition.name
        )
        return abstract_step

    else:
        steps_dict: dict[str, ABSTRACT_STEP] = _retrieve_all_functions(module)
        return steps_dict


def _load_module(import_definition: Import) -> ModuleType:
    module_path = Path(import_definition.module)
    if module_path.is_file():
        return importlib.machinery.SourceFileLoader(
            module_path.stem, import_definition.module
        ).load_module()

    raise ValueError("Module '" + str(import_definition.module) + "' non-existent")


def _retrieve_function(
    module: ModuleType, import_definition_name: str
) -> ABSTRACT_STEP:
    implementation = getattr(module, import_definition_name)
    if inspect.isclass(implementation):
        return _check_stateful_step(implementation, import_definition_name)
    else:
        return implementation


def _retrieve_all_functions(
    module: ModuleType,
) -> dict[str, ABSTRACT_STEP]:
    members = inspect.getmembers(module)
    public_functions: dict[str, Callable[[ImmutableModel], ImmutableModel]] = {
        member[0]: member[1]
        for member in members
        if inspect.isfunction(member[1]) and not member[0].startswith("_")
    }
    public_stateful_steps: dict[str, type[StatefulCallable[Any, Any]]] = {
        member[0]: member[1]
        for member in members
        if inspect.isclass(member[1])
        and issubclass(member[1], StatefulCallable)
        and member[1] != StatefulCallable
        and not member[0].startswith("_")
    }
    return {
        name: func
        for name, func in {**public_functions, **public_stateful_steps}.items()
    }


def _check_stateful_step(
    to_check: type[Any], import_definition_name: str
) -> type[StatefulCallable[Any, Any]]:
    if not issubclass(to_check, StatefulCallable):
        raise TypeError(
            "Implementation '"
            + str(import_definition_name)
            + "' is not a subclass of StatefulCallable."
        )
    return cast(type[StatefulCallable[Any, Any]], to_check)


def _is_specific_import(import_definition_name: Optional[str]) -> TypeGuard[str]:
    return bool(import_definition_name)
