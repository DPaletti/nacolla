from __future__ import annotations
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Type, Union, cast
from pydantic.types import StrictStr
from nacolla.models import ImmutableModel
from importlib import import_module
import inspect
import sys
import json
from nacolla.parsing.implementation_map_file_specification import (
    ImplementationMapSpecification,
    Import,
)
from nacolla.stateful_callable import StatefulCallable


class Implementation(ImmutableModel):

    callable: Union[
        Callable[[ImmutableModel], ImmutableModel],
        Type[StatefulCallable[Any, Any]],
        List[
            Union[
                Callable[[ImmutableModel], ImmutableModel],
                Type[StatefulCallable[Any, Any]],
            ]
        ],
    ]

    def __init__(self, import_definition: Import):
        module: ModuleType

        try:
            module = import_module(import_definition.module)
        except (ModuleNotFoundError, TypeError):
            module_path: Path = Path(import_definition.module)
            if not module_path.exists():
                raise ValueError("Cannot find " + import_definition.module)

            sys.path.append(str(module_path.parents[0]))

            module: ModuleType = import_module(
                name=module_path.stem, package=str(module_path.parents[0])
            )

        if import_definition.name:
            implementation = getattr(module, import_definition.name)
            if inspect.isclass(implementation):
                self._set_callable(
                    Implementation._check_stateful_step(
                        implementation, import_definition
                    )
                )
            else:
                self._set_callable(implementation)

        else:
            members = inspect.getmembers(module)
            public_functions: Set[Callable[[ImmutableModel], ImmutableModel]] = {
                member[1]
                for member in members
                if inspect.isfunction(member[1]) and not member[0].startswith("_")
            }
            public_stateful_steps: List[Type[StatefulCallable[Any, Any]]] = [
                member[1]
                for member in members
                if inspect.isclass(member[1])
                and issubclass(member[1], StatefulCallable)
                and member[1] != StatefulCallable
                and not member[0].startswith("_")
            ]
            self._set_callable(list(public_functions.union(public_stateful_steps)))

    def _set_callable(
        self,
        to_set: Union[
            Callable[[ImmutableModel], ImmutableModel],
            Type[StatefulCallable[Any, Any]],
            Iterable[
                Union[
                    Callable[[ImmutableModel], ImmutableModel],
                    Type[StatefulCallable[Any, Any]],
                ]
            ],
        ],
    ):
        object.__setattr__(self, "callable", to_set)

    @staticmethod
    def _check_stateful_step(
        to_check: Type[Any], import_definition: Import
    ) -> Type[StatefulCallable[Any, Any]]:
        if not issubclass(to_check, StatefulCallable):
            raise TypeError(
                "Implementation '"
                + str(import_definition.name)
                + "' from '"
                + str(import_definition.module)
                + "' is not a subclass of StatefulCallable."
            )
        return cast(Type[StatefulCallable[Any, Any]], to_check)


class ImplementationMap(ImmutableModel):
    implementations: Dict[StrictStr, Implementation]

    def __init__(self, specification: ImplementationMapSpecification):
        implementation_dict: Dict[str, Implementation] = {}
        for step in specification.implementations:
            step_callable: Import = Import(**dict(step.callable))
            if step.name in implementation_dict.keys():
                raise ValueError(
                    "Steps must have unique names, encountered '"
                    + step.name
                    + "' twice"
                )
            implementation_dict[step.name] = Implementation(
                import_definition=step_callable  # type: ignore
            )

        object.__setattr__(self, "implementations", implementation_dict)

    def __getitem__(self, step_name: str) -> Implementation:
        return self.implementations[step_name]

    def get(self, step_name: str) -> Optional[Implementation]:
        try:
            return self.implementations[step_name]
        except KeyError:
            return None


def parse_implementation_map(
    implementation_map_file: Path,
) -> ImplementationMap:
    return ImplementationMap(
        specification=ImplementationMapSpecification(
            **json.loads(implementation_map_file.read_text())
        )
    )
