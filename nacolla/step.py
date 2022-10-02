from __future__ import annotations
from typing import (
    Callable,
    Generic,
    TypeVar,
)

from pydantic.types import StrictStr
from nacolla.models import GenericImmutableModel, ImmutableModel

_T = TypeVar("_T", bound=ImmutableModel)
_S = TypeVar("_S", bound=ImmutableModel)


class Step(GenericImmutableModel, Generic[_T, _S]):
    """A generic data transformation"""

    apply: Callable[[_T], _S]
    next: Callable[[_S], "Step[_S, ImmutableModel]"]
    name: StrictStr
