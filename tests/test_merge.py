from __future__ import annotations
from typing import Union, cast
from nacolla.operations import merge
import pytest
from nacolla.utilities import unwrap_union
from tests.mock_models import (
    WrappedInt,
    WrappedDict,
    WrappedFloat,
    WrappedSet,
    WrappedString,
)
from tests.mock_steps import make_counter_step, make_steps, make_string_adder_step


def test_merge_incompatible_interfaces():
    s1, _ = make_steps()

    with pytest.raises(TypeError):
        merge(s1, s1)

    counter_step = make_counter_step()
    with pytest.raises(TypeError):
        merge(s1, counter_step)


def test_merge_singledispatch_default_implementation():
    s1, s2 = make_steps()

    merged = merge(s1, s2)

    with pytest.raises(NotImplementedError):
        merged(WrappedSet(a_set={1, 2, 3}))  # type: ignore

    with pytest.raises(KeyError):
        next(merged)[WrappedSet]  # type: ignore


def test_merge_resulting_interface_types():
    s1, s2 = make_steps()
    merged = merge(s1, s2)

    assert merged.input_interface == unwrap_union(Union[WrappedInt, WrappedFloat])  # type: ignore
    assert merged.output_interface == unwrap_union(Union[WrappedString, WrappedDict])  # type: ignore


def test_merge_resulting_transformation():
    counter = make_counter_step()
    str_adder = make_string_adder_step()

    merged = merge(counter, str_adder)

    assert merged.input_interface == unwrap_union(Union[WrappedInt, WrappedFloat, WrappedString])  # type: ignore
    assert merged.output_interface == unwrap_union(Union[WrappedInt, WrappedString])  # type: ignore

    assert cast(WrappedInt, merged(WrappedInt(a_int=1))).a_int == 1
    assert cast(WrappedInt, merged(WrappedFloat(a_float=1.0))).a_int == 3
    assert (
        cast(WrappedString, merged(WrappedString(a_string="some_string"))).a_string
        == "some_string"
    )
    assert (
        cast(WrappedString, merged(WrappedString(a_string="_some_string"))).a_string
        == "some_string_some_string"
    )
