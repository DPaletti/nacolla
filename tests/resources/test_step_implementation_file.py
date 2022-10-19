from tests.mock_models import WrappedFloat, WrappedInt, WrappedString
from nacolla import StatefulStep


def float_to_int(f: WrappedFloat) -> WrappedInt:
    return WrappedInt(a_int=int(f.a_float))


class A(StatefulStep[WrappedString, WrappedString]):
    def __init__(self) -> None:
        super().__init__()
        self.storage = ""

    def str_append(self, s: WrappedString) -> WrappedString:
        self.storage += s.a_string
        return WrappedString(a_string=self.storage)
