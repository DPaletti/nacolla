from typing import List
from pydantic.types import StrictStr
from nacolla.models import ImmutableModel


class Import(ImmutableModel):
    module: StrictStr
    name: StrictStr


class ImplementationSpecification(ImmutableModel):
    callable: Import
    name: StrictStr


class ImplementationMapSpecification(ImmutableModel):
    implementations: List[ImplementationSpecification]
