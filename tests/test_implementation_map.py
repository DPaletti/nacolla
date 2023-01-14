from typing import cast
import pytest
from pathlib import Path
from nacolla.parsing.implementation_map_file_specification import (
    Import,
)

from nacolla.parsing.parse_implementation import parse_implementation

from nacolla.parsing.parse_implementation_map import (
    IMPLEMENTATION_MAP,
    parse_implementation_map,
)
from tests.mock_models import WrappedFloat, WrappedInt, WrappedString


def test_mixed_file_and_selected_function():
    implementation_map: IMPLEMENTATION_MAP = parse_implementation_map(
        Path("resources/test_implementation_map.json")
    )

    assert (
        cast(
            WrappedString,
            implementation_map["step1"](WrappedString(a_string="_postfix")),
        ).a_string
        == "my_prefix_in_dict_postfix"
    )
    assert (
        cast(WrappedInt, implementation_map["step1"](WrappedFloat(a_float=2.0))).a_int
        == 2
    )
    assert (
        cast(WrappedString, implementation_map["step2"](WrappedInt(a_int=1))).a_string
        == "1"
    )
    assert (
        cast(
            WrappedString,
            implementation_map["step3"](WrappedString(a_string="_postfix")),
        ).a_string
        == "my_prefix_postfix"
    )


def test_non_existent_module():
    with pytest.raises(ValueError):
        parse_implementation(import_definition=Import(module="not_existent", name=""))


def test_non_stateful_step_class():
    with pytest.raises(TypeError):
        parse_implementation(
            import_definition=Import(
                module="resources/test_step_implementation_wrong_class.py", name="A"
            )
        )


def test_repeated_name():
    with pytest.raises(ValueError):
        parse_implementation_map(
            Path("resources/test_implementation_map_repeated.json")
        )
