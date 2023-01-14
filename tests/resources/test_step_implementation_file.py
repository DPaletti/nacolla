from typing import Union
from tests.mock_models import WrappedEndString, WrappedFloat, WrappedInt, WrappedString
from nacolla import StatefulStep


def float_to_int(f: WrappedFloat) -> WrappedInt:
    return WrappedInt(a_int=int(f.a_float))


class A(StatefulStep[WrappedString, Union[WrappedString, WrappedEndString]]):
    def __init__(self, prefix: str) -> None:
        super().__init__()
        self.storage = prefix

    def str_append(self, s: WrappedString) -> Union[WrappedString, WrappedEndString]:

        self.storage += s.a_string
        if len(self.storage) < 20:
            return WrappedString(a_string=self.storage)
        else:
            return WrappedEndString(a_string=self.storage)
