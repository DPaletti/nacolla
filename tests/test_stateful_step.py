from __future__ import annotations
from typing import Union

import pytest
from nacolla.stateful_step import StatefulStep
from nacolla.type_utilities import unwrap_union
from tests.mock_models import WrappedFloat, WrappedInt
from tests.mock_steps import make_counter_step


def test_stateful_step_from_class():

    step = make_counter_step()

    assert step.input_interface == unwrap_union(Union[WrappedInt, WrappedFloat])  # type: ignore
    assert step.output_interface == unwrap_union(WrappedInt)

    assert step(WrappedInt(a_int=1)).a_int == 1
    assert step(WrappedInt(a_int=1)).a_int == 2
    assert step(WrappedFloat(a_float=1.0)).a_int == 4
    with pytest.raises(NotImplementedError):
        assert step(1)  # type: ignore


def test_invalid_class():
    class NoPublicMethods(StatefulStep):  # type: ignore
        def __init__(self) -> None:
            super().__init__()

    with pytest.raises(TypeError):
        no_public_methods = NoPublicMethods()  # type: ignore
