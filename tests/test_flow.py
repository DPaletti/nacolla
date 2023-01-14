from pathlib import Path
from typing import List, Union, cast
from nacolla.flow import Flow
from nacolla.models import ImmutableModel
from nacolla.parsing.parse_flow import parse_flow
from nacolla.parsing.parse_implementation_map import (
    IMPLEMENTATION_MAP,
    parse_implementation_map,
)
from nacolla.step import Step
from tests.mock_models import WrappedEndString, WrappedFloat, WrappedInt, WrappedString
from tests.mock_steps import make_counter_step


def test_flow():
    counter_step_1: Step[
        Union[WrappedInt, WrappedFloat], WrappedInt
    ] = make_counter_step()

    counter_step_2: Step[
        Union[WrappedInt, WrappedFloat], WrappedInt
    ] = make_counter_step()

    counter_step_1.concatenate(counter_step_2, WrappedInt)
    flow: Flow[WrappedInt] = Flow(root=counter_step_1, source=WrappedInt(a_int=2))
    steps: List[Step[ImmutableModel, ImmutableModel]] = []
    messages: List[ImmutableModel] = []
    for step in flow:
        steps.append(step)
        messages.append(flow.current_message)
    assert steps[0] == counter_step_2
    assert cast(WrappedInt, messages[0]).a_int == 2
    assert cast(WrappedInt, flow.current_message).a_int == 2


def test_flow_parsing():
    implementation_map: IMPLEMENTATION_MAP = parse_implementation_map(
        Path("resources/test_implementation_map.json")
    )
    flow: Flow[WrappedInt] = parse_flow(
        Path("./resources/test_flow.toml"),
        implementation_map=implementation_map,
        source=WrappedFloat(a_float=2.0),
    )

    steps: List[Step[ImmutableModel, ImmutableModel]] = [flow.current_step]
    messages: List[ImmutableModel] = [WrappedFloat(a_float=2.0)]
    for step in flow:
        steps.append(step)
        messages.append(flow.current_message)

    assert steps[0] == implementation_map["step1"]
    assert steps[1] == implementation_map["step2"]
    assert steps[2] == implementation_map["step3"]
    assert messages[0] == WrappedFloat(a_float=2.0)
    assert messages[1] == WrappedInt(a_int=2)
    assert messages[2] == WrappedString(a_string="2")
    assert messages[3] == WrappedString(a_string="my_prefix2")
    assert flow.current_message == WrappedEndString(a_string="my_prefix2my_prefix2")
