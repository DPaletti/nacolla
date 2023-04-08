from __future__ import annotations
from typing import Generic, Iterator, TypeVar, Union, cast
from nacolla.models import ImmutableModel
from nacolla.step import End, Step
import copy

_SOURCE = TypeVar("_SOURCE", bound=ImmutableModel)


class Flow(Iterator[Step[ImmutableModel, ImmutableModel]], Generic[_SOURCE]):
    def __init__(self, root: Step[_SOURCE, ImmutableModel], source: _SOURCE) -> None:
        self.__current_step: Step[ImmutableModel, ImmutableModel] = root
        self.__current_message: ImmutableModel = source

    @property
    def current_message(self):
        return copy.deepcopy(self.__current_message)

    @property
    def current_step(self):
        return self.__current_step

    def __next__(self) -> Step[ImmutableModel, ImmutableModel]:
        self.__current_message = self.__current_step(self.__current_message)
        self.__current_step = self._stop(
            self.__current_step.next_step(type(self.__current_message))
        )
        return self.__current_step

    def __iter__(self) -> Iterator[Step[ImmutableModel, ImmutableModel]]:
        return self

    def _stop(
        self, step: Union[Step[ImmutableModel, ImmutableModel], End]
    ) -> Step[ImmutableModel, ImmutableModel]:
        if type(step) is End:
            raise StopIteration
        else:
            return cast(Step[ImmutableModel, ImmutableModel], step)
