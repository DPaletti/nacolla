from typing import Union

import pytest
from nacolla.operations.concatenate import concatenate
from nacolla.step import End, Step
from tests.mock_models import WrappedFloat, WrappedString
from tests.mock_steps import make_steps


def test_concatenate_simple_steps():
    def f(s: Union[WrappedString, WrappedFloat]) -> WrappedString:
        return WrappedString(a_string=str(s))

    s1, _ = make_steps()

    s2: Step[Union[WrappedString, WrappedFloat], WrappedString] = Step[
        Union[WrappedString, WrappedFloat], WrappedString
    ](apply=f, next={WrappedString: End()}, name="str_to_str")

    concatenated = concatenate(s1, s2, WrappedString)

    assert str(concatenated) == str(s1)
    assert concatenated.input_interface == s1.input_interface
    assert concatenated.output_interface == s1.output_interface
    assert next(concatenated)[WrappedString] == s2


def test_concatenate_non_existent_connection():
    def f(s: WrappedString) -> WrappedString:
        return s

    _, s1 = make_steps()

    s2: Step[WrappedString, WrappedString] = Step[WrappedString, WrappedString](
        apply=f, next={WrappedString: End()}, name="str_to_str"
    )

    with pytest.raises(TypeError):
        concatenate(s1, s2, WrappedString)  # type: ignore
