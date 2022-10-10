from __future__ import annotations
from typing import Generic, Iterator, TypeVar, Union, cast
from nacolla.models import ImmutableModel
from nacolla.step import End, Step

_SOURCE = TypeVar("_SOURCE", bound=ImmutableModel)


class Flow(Iterator[Step[ImmutableModel, ImmutableModel]], Generic[_SOURCE]):
    def __init__(self, root: Step[_SOURCE, ImmutableModel], source: _SOURCE) -> None:
        self.current_step: Step[ImmutableModel, ImmutableModel] = root
        self.current_message: ImmutableModel = source

    def __next__(self) -> Step[ImmutableModel, ImmutableModel]:
        self.current_message = self.current_step(self.current_message)
        self.current_step = self._stop(
            next(self.current_step)[type(self.current_message)]
        )
        return self.current_step

    def __iter__(self) -> Iterator[Step[ImmutableModel, ImmutableModel]]:
        return self

    def _stop(
        self, step: Union[Step[ImmutableModel, ImmutableModel], End]
    ) -> Step[ImmutableModel, ImmutableModel]:
        if type(step) is End:
            raise StopIteration
        else:
            return cast(Step[ImmutableModel, ImmutableModel], step)
