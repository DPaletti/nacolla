from pathlib import Path
from typing import Dict, Optional, Tuple, Type, TypeVar, Union
from typing_extensions import TypeGuard
from nacolla.models import ImmutableModel
from nacolla.parsing.parse_implementation_map import (
    IMPLEMENTATION_MAP,
)
from nacolla.step import Step
from nacolla.flow import Flow
import toml

_SOURCE = TypeVar("_SOURCE", bound=ImmutableModel)
_MAPPING = Dict[Type[ImmutableModel], Step[ImmutableModel, ImmutableModel]]
_FLOW_DESCRIPTION_ITEM = Union[str, Dict[str, str]]


def parse_flow(
    flow_description: Path, implementation_map: IMPLEMENTATION_MAP, source: _SOURCE
) -> Flow[_SOURCE]:
    root, mapping = _validate_flow_description(
        toml.loads(flow_description.read_text()), implementation_map
    )
    for step_name, step_mapping in mapping.items():
        step = implementation_map[step_name]

        for port, destination_step in step_mapping.items():
            step.concatenate(destination_step, port)

    return Flow(root=root, source=source)


def _validate_flow_description(
    flow_description: Dict[str, _FLOW_DESCRIPTION_ITEM],
    implementation_map: IMPLEMENTATION_MAP,
) -> Tuple[Step[ImmutableModel, ImmutableModel], Dict[str, _MAPPING],]:

    root = flow_description.get("root")
    if not _root_is_str(root):
        raise ValueError(
            "Invalid root provided "
            + str(root)
            + " please specify a root in the flow description file as the name of a step in the implementation file.\n"
            + "Root is a reserved name do not use it for any of your steps."
        )

    root_step: Step[ImmutableModel, ImmutableModel] = _validate_root(
        root_step_name=root,
        implementation_map=implementation_map,
        flow_description=flow_description,
    )
    mapping: Dict[str, _MAPPING] = {}

    for step_name, plain_mapping in {
        step_name: plain_mapping
        for step_name, plain_mapping in flow_description.items()
        if step_name != "root"
    }.items():
        step = implementation_map.get(step_name)
        if step is None:
            raise ValueError(
                "Could not find '" + str(step_name) + "' in implementation map."
            )

        step_ports: Dict[str, Type[ImmutableModel]] = {
            output_port.__name__: output_port for output_port in step.output
        }

        if not _is_mapping_dict(plain_mapping):
            raise ValueError(
                "Malformed mapping for "
                + str(step_name)
                + " got "
                + str(plain_mapping)
                + ".\n"
                + "Expected a mapping from type to step."
            )

        step_mapping: _MAPPING = {}
        for port_name, destination_step_name in plain_mapping.items():
            port = step_ports.get(port_name)
            if port is None:
                raise ValueError(
                    "Could not find '"
                    + str(port_name)
                    + "' among the types handled by '"
                    + str(step_name)
                )
            destination_step = implementation_map.get(destination_step_name)
            if destination_step is not None:
                step_mapping[port] = destination_step
        mapping[step.name] = step_mapping

    return root_step, mapping


def _is_mapping_dict(
    dict_to_validate: Union[str, Dict[str, str]]
) -> TypeGuard[Dict[str, str]]:
    if type(dict_to_validate) is not dict:
        return False

    for value in dict_to_validate.values():
        if type(value) is not str:
            return False
    return True


def _root_is_str(root: Optional[_FLOW_DESCRIPTION_ITEM]) -> TypeGuard[str]:
    return root is None or root is not str


def _validate_root(
    root_step_name: str,
    implementation_map: IMPLEMENTATION_MAP,
    flow_description: Dict[str, _FLOW_DESCRIPTION_ITEM],
) -> Step[ImmutableModel, ImmutableModel]:

    root: Step[ImmutableModel, ImmutableModel] = implementation_map[root_step_name]

    if root is None:
        raise ValueError(
            "Please specify a valid root in the description file, '"
            + str(root_step_name)
            + "' could not be found in the implementation file"
        )
    if root.name not in flow_description:
        raise ValueError(
            "Root step '"
            + str(root.name)
            + "' must be among the steps included in the flow '"
            + str(flow_description.keys())
            + "'."
        )
    return root
