import pytest
from nacolla.parsing import parse_implementation_map, ImplementationMap
from pathlib import Path
from nacolla.parsing.implementation_map_file_specification import (
    ImplementationMapSpecification,
    Import,
)

from nacolla.parsing.parse_implementation_map import Implementation
import json


def test_mixed_file_and_selected_function():
    implementation_map: ImplementationMap = parse_implementation_map(
        Path("resources/test_implementation_map.json")
    )
    assert implementation_map.get("step1") is not None
    assert implementation_map.get("step2") is not None
    assert implementation_map.get("step0") is None
    assert callable(implementation_map["step2"].callable)
    assert type(implementation_map["step1"].callable) is list


def test_non_existent_module():
    with pytest.raises(ValueError):
        Implementation(import_definition=Import(module="not_existent", name=""))


def test_non_stateful_step_class():
    with pytest.raises(TypeError):
        Implementation(
            import_definition=Import(
                module="resources/test_step_implementation_wrong_class.py", name="A"
            )
        )


def test_repeated_name():
    with pytest.raises(ValueError):
        repeated_key = json.loads(
            Path("resources/test_implementation_map.json").read_text()
        )
        repeated_key["implementations"].append(
            {"callable": {"module": "some", "name": "name"}, "name": "step1"}
        )

        ImplementationMap(specification=ImplementationMapSpecification(**repeated_key))
