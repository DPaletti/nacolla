from __future__ import annotations
from typing import Dict, Set
from pydantic.types import StrictFloat, StrictInt, StrictStr
from nacolla.models import ImmutableModel


class WrappedString(ImmutableModel):
    a_string: StrictStr


class WrappedEndString(ImmutableModel):
    a_string: StrictStr


class WrappedInt(ImmutableModel):
    a_int: StrictInt


class WrappedFloat(ImmutableModel):
    a_float: StrictFloat


class WrappedDict(ImmutableModel):
    a_dict: Dict[str, float]


class WrappedSet(ImmutableModel):
    a_set: Set[int]
