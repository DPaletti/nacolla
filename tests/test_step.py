from nacolla.step import Step
from tests.mock_models import WrappedFloat
import pytest


def test_step_has_single_input():
    def f(i: int, j: float) -> float:
        return i + j

    with pytest.raises(TypeError):
        Step(apply=f, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_has_input_annotations():
    with pytest.raises(TypeError):
        Step(apply=lambda x: x, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_has_output_annotations():
    def f(i: WrappedFloat):
        return i

    with pytest.raises(TypeError):
        Step(apply=f, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_interface_inspection():
    def f(i: WrappedFloat) -> WrappedFloat:
        return i

    s0: Step[WrappedFloat, WrappedFloat] = Step(apply=f, next=f, name="valid step")
    assert s0.input_interface == {WrappedFloat}
    assert s0.output_interface == {WrappedFloat}
