from __future__ import annotations
from typing import Union
from nacolla.operations import merge
from nacolla.step import Stateful, Step
import pytest
from tests.mock_models import (
    WrappedInt,
    WrappedDict,
    WrappedFloat,
    WrappedSet,
    WrappedString,
)


def _int_to_str(input: WrappedInt) -> WrappedString:
    return WrappedString(a_string=str(input.a_int))


def _annotated_identity_str(input: WrappedString) -> WrappedString:
    return input


def _annotated_identity_dict(input: WrappedDict) -> WrappedDict:
    return input


def _float_to_dict(input: WrappedFloat) -> WrappedDict:
    return WrappedDict(a_dict={"a_value": input.a_float})


_s1: Step[WrappedInt, WrappedString] = Step(
    apply=_int_to_str, next=_annotated_identity_str, name="int_to_str"
)

_s2: Step[WrappedFloat, WrappedDict] = Step(
    apply=_float_to_dict, next=_annotated_identity_dict, name="float_to_dict"
)


def test_merge_incompatible_interfaces():

    with pytest.raises(TypeError):
        merge(_s1, _s1)


def test_merge_singledispatch_default_implementation():

    merged = merge(_s1, _s2)

    with pytest.raises(NotImplementedError):
        merged.apply(WrappedSet(a_set={1, 2, 3}))  # type: ignore

    with pytest.raises(NotImplementedError):
        merged.next(WrappedSet(a_set={1, 2, 3}))  # type: ignore


def test_merge_resulting_interface_types():
    merged = merge(_s1, _s2)

    assert merged.input_interface is Union["WrappedInt", "WrappedFloat"]
    assert merged.output_interface is Union["WrappedString", "WrappedDict"]


def test_merge_stateful_steps():
    ss1: Stateful[WrappedInt, WrappedString, WrappedInt] = Stateful(
        apply=_int_to_str,
        next=_annotated_identity_str,
        name="int_to_str",
        state=WrappedInt(a_int=1),
    )

    with pytest.raises(TypeError):
        merge(ss1, _s2)
