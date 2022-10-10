from typing import List, Union, cast
from nacolla.flow import Flow
from nacolla.models import ImmutableModel
from nacolla.step import Step
from tests.mock_models import WrappedFloat, WrappedInt
from tests.mock_steps import make_counter_step
from nacolla.operations import concatenate


def test_flow():
    counter_step_1: Step[
        Union[WrappedInt, WrappedFloat], WrappedInt
    ] = make_counter_step()

    counter_step_2: Step[
        Union[WrappedInt, WrappedFloat], WrappedInt
    ] = make_counter_step()

    counter_step_1 = concatenate(counter_step_1, counter_step_2, WrappedInt)
    flow: Flow[WrappedInt] = Flow(root=counter_step_1, source=WrappedInt(a_int=2))
    steps: List[Step[ImmutableModel, ImmutableModel]] = []
    messages: List[ImmutableModel] = []
    for step in flow:
        steps.append(step)
        messages.append(flow.current_message)
    assert steps[0] == counter_step_2
    assert cast(WrappedInt, messages[0]).a_int == 2
    assert cast(WrappedInt, flow.current_message).a_int == 4
