from __future__ import annotations

from pydantic.error_wrappers import ValidationError
from nacolla.step import End, Step
from tests.mock_models import WrappedFloat, WrappedInt
import pytest

from tests.mock_steps import make_steps


def test_step_has_single_input():
    def f(i: int, j: float) -> float:
        return i + j

    with pytest.raises(ValidationError):
        Step(apply=f, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_has_input_annotations():
    with pytest.raises(ValidationError):
        Step(apply=lambda x: x, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_has_output_annotations():
    def f(i: WrappedFloat):
        return i

    with pytest.raises(ValidationError):
        Step(apply=f, next=lambda x: x, name="invalid step")  # type: ignore


def test_step_interface_inspection():
    def f(i: WrappedFloat) -> WrappedFloat:
        return i

    s0: Step[WrappedFloat, WrappedFloat] = Step(
        apply=f, next={WrappedFloat: End()}, name="valid step"
    )
    assert s0.input_interface == {WrappedFloat}
    assert s0.output_interface == {WrappedFloat}


def test_end():
    with pytest.raises(StopIteration):
        next(End())


def test_reassemble_interface():
    s0, _ = make_steps()
    with pytest.raises(ValueError):
        s0.assemble_interface(
            None,
            {
                "input_interface": {"some"},
                "output_interface": {"some other"},
                "apply": s0.apply,
            },
        )


def test_non_immutable_interface():
    def f(i: WrappedFloat) -> float:
        return i.a_float

    with pytest.raises(ValidationError):
        Step(apply=f, next={float: End()}, name="Invalid interface step")  # type: ignore


def test_dangling_mapping():
    def f(i: WrappedFloat) -> WrappedFloat:
        return i

    with pytest.raises(ValidationError):
        Step(apply=f, next={}, name="Invalid Mapping step")  # type: ignore


def test_incompatible_mapping():
    def f(i: WrappedFloat) -> WrappedFloat:
        return i

    def g(i: WrappedInt) -> WrappedInt:
        return i

    with pytest.raises(ValidationError):
        Step(apply=f, next={WrappedFloat: Step(apply=g, next={WrappedInt: End()}, name="...")}, name="Invalid Mapping step")  # type: ignore
