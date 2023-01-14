from typing import TypeVar

from nacolla.models import ImmutableModel


INTERFACE = TypeVar("INTERFACE", bound=ImmutableModel)
INPUT_INTERFACE = TypeVar("INPUT_INTERFACE", bound=ImmutableModel, contravariant=True)
OUTPUT_INTERFACE = TypeVar("OUTPUT_INTERFACE", bound=ImmutableModel, covariant=True)
